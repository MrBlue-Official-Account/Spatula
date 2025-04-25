"""
    # Selenium class - Email scrapper
"""
# pylint: disable=C0301,W0702,W0718

import re
import logging
import random
import time
import os
import sys
from typing import Set, Deque, Tuple
from urllib.parse import urljoin, urlparse
from collections import deque

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import tldextract
from Modules.banner import BRIGHT, RED, GREEN, WHITE, RESET

# ─── Actulizacion de 'Chromedriver.exe' ─────────────────────────────────────


# ─── Ingresar valores correctos ─────────────────────────────────────────────
def es_url_valida(url: str) -> bool:
    """Verifica si una URL tiene un esquema y dominio válidos."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

# ─── Configuración de logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

# ─── Handler de señal Ctrl+C ────────────────────────────────────────────────────

# Controlador global de la instancia de scraper
CURRENT_SCRAPER = None
_SIGINT_HANDLED = False
_COLLECTED_RESULTS = False

def handle_sigint(_, __): # pylint: disable=C0116
    global _SIGINT_HANDLED

    if _SIGINT_HANDLED:
        return
    _SIGINT_HANDLED = True

    if CURRENT_SCRAPER:
        resultados = CURRENT_SCRAPER.get_results()
        if resultados:
            for email in sorted(resultados):
                print(f"• {email}")
        else:
            print(f"{BRIGHT}{RED}No se encontraron emails.{RESET}")
        CURRENT_SCRAPER.close()

    sys.exit(0)

# ─── Clase principal ────────────────────────────────────────────────────────────
class EmailScraper:
    """Extract emails with Selenium"""
    EMAIL_REGEX = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]
    CHROMEDRIVER_PATH = os.path.join('.', 'chromedriver-win64', 'chromedriver.exe')
    INVALID_TLDS: Set[str] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico', 'bmp'}

    def __init__(
        self,
        base_url: str,
        max_depth: int = 2,
        headless: bool = True,
        max_pages: int = 0,
        page_timeout: int = 15,
        delay: float = 1.0,
        hide=False
    ):
        self.hide = hide
        self.base_url = base_url.rstrip('/')  # normalizar sin slash final
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.page_timeout = page_timeout
        self.delay = delay

        self.pages_scanned = 0
        self.visited_urls: Set[str] = set()
        self.emails: Set[str] = set()

        domain_info = tldextract.extract(self.base_url)
        self.registered_domain = f"{domain_info.domain}.{domain_info.suffix}"

        self.driver = self._init_webdriver(headless)
        self._validate_domain()
        self._check_robots_txt()

    def _init_webdriver(self, headless: bool) -> webdriver.Chrome:
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        # options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--use-angle=swiftshader')
        options.add_argument('--enable-unsafe-swiftshader')
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-webgl")
        options.add_argument("--use-angle=swiftshader")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument(f"user-agent={random.choice(self.DEFAULT_USER_AGENTS)}")

        null_dev = 'NUL' if os.name == 'nt' else '/dev/null'
        service = ChromeService(executable_path=self.CHROMEDRIVER_PATH, log_path=null_dev)
        driver = webdriver.Chrome(service=service, options=options)

        driver.set_page_load_timeout(self.page_timeout)
        driver.implicitly_wait(5)
        return driver

    def _validate_domain(self) -> None:
        if not self.registered_domain:
            raise ValueError('⚠️ El dominio no esta registrado o es invalido')

    def _check_robots_txt(self) -> None:
        robots_url = urljoin(self.base_url, '/robots.txt')
        try:
            self.driver.get(robots_url)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except Exception:
            pass

    def _random_delay(self) -> None:
        if self.delay > 0:
            time.sleep(self.delay)

    def _is_valid_email(self, email: str) -> bool:
        try:
            _, dom = email.split('@', 1)
        except ValueError:
            return False
        if '.' not in dom:
            return False
        tld = dom.rsplit('.', 1)[1].lower()
        return tld not in self.INVALID_TLDS

    def _extract_links(self, current_url: str) -> Set[str]:
        links: Set[str] = set()
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'a')
            for el in elements:
                try:
                    href = el.get_attribute('href')
                except StaleElementReferenceException:
                    continue
                if not href:
                    continue
                parsed = urlparse(href)
                if parsed.scheme not in ('http', 'https'):
                    continue
                if tldextract.extract(href).registered_domain != self.registered_domain:
                    continue
                links.add(href)
        except WebDriverException as e:
            logger.error('❗ %s%sError extrayendo enlaces: %s%s%s', BRIGHT,RED, WHITE,e,RESET)
        return links

    def _scrape_emails(self, content: str) -> None:
        found = set(self.EMAIL_REGEX.findall(content))
        valid = {e for e in found if self._is_valid_email(e)}
        new = valid - self.emails
        if new:
            logger.info('%s%sEncontrado(s) %s%s %semail(s):%s', BRIGHT,GREEN, WHITE,len(new), GREEN,RESET)
            for e in sorted(new):
                logger.info('    # %s', e)
            self.emails.update(new)

    def _process_page(self, url: str) -> None:
        if url in self.visited_urls:
            return
        if 0 < self.max_pages <= self.pages_scanned:
            raise StopIteration
        self.visited_urls.add(url)
        self.pages_scanned += 1

        if not self.hide:
            logger.info('%s%sProcesando (%s): %s%s', BRIGHT,WHITE, self.pages_scanned, url, RESET)
        try:
            self.driver.set_page_load_timeout(self.page_timeout)  # << asegurar timeout
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            self._random_delay()
            self._scrape_emails(self.driver.page_source)
        except TimeoutException:
            logger.warning('⚠️ Timeout al cargar %s, omitiendo.', url)
        except StopIteration:
            raise
        except WebDriverException as e:
            logger.error('❗ %s%sWebDriverException en %s%s: %s%s', BRIGHT, RED, GREEN, url, RESET, e)
        except Exception as e:
            logger.error('❗ %s%sError procesando %s%s: %s%s',BRIGHT,RED,WHITE, url, e, RESET)

    def run(self) -> None:
        global current_scraper
        current_scraper = self
        queue: Deque[Tuple[str, int]] = deque([(self.base_url, 0)])
        while queue:
            url, depth = queue.popleft()
            if depth > self.max_depth:
                continue
            try:
                self._process_page(url)
            except StopIteration:
                break
            for link in self._extract_links(url):
                if link not in self.visited_urls:
                    queue.append((link, depth + 1))
        logger.info("%s%sExploracion completada. %sTotal escaneado: %s%s%s pagina(s). Emails encontrados: %s%s%s",\
            BRIGHT,GREEN,WHITE,GREEN,self.pages_scanned,WHITE,GREEN,len(self.emails),RESET)

    def get_results(self) -> Set[str]:
        """Return emails results"""
        return self.emails

    def close(self) -> None:
        """Cerrar Navegador"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print('❗ %s%sError cerrando WebDriver: %s\n%s',BRIGHT,WHITE, e, RESET)
        # except KeyboardInterrupt:
        #     print(f"{BRIGHT}{YELLOW}Saliendo...{RESET}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
