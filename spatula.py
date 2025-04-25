"""
    # call Selenium class - Email scrapper
"""
# pylint: disable=C0115,C0301,C0103,W0718

import argparse
import sys
from selenium.common.exceptions import WebDriverException
from Modules.banner import BANNER, BRIGHT, RED, YELLOW, MAGENTA, GREEN, WHITE, RESET
from Modules.emails_scrapper import EmailScraper
from Modules.update import perform_update, __version__

class BannerArgumentParser(argparse.ArgumentParser):
    """ArgumentParser que imprime el BANNER antes de la ayuda."""
    def print_help(self, file=None):
        # Primero el banner
        print(BANNER,'\n')
        # Luego la ayuda normal
        super().print_help(file)

if __name__ == '__main__':
    parser = BannerArgumentParser(
        description="Herramienta de scraping de correos electrónicos."
    )
    # parser = argparse.ArgumentParser(description='Web Email Scraper')
    # parser = argparse.ArgumentParser(description="Herramienta de scraping de correos electronicos.")
    parser.add_argument("url", nargs='?', help="URL base a explorar (por ejemplo: https://example.com)")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Profundidad máxima de rastreo (por defecto: 2)")
    parser.add_argument("-sb", "--subdomains", type=int, default=0, help="Número máximo de páginas a visitar (0 = ilimitado)")
    parser.add_argument("-t", "--timeout", type=int, default=15, help="Timeout de carga de página (segundos)")
    parser.add_argument("--delay", type=float, default=1.0, help="Retraso entre peticiones (segundos)")
    parser.add_argument("-v", "--visible", action="store_false", help="Mostrar navegador (modo visible)")
    parser.add_argument("-hd", "--hide", action="store_true", help="Ocultar los enlaces durante la navegación")
    parser.add_argument("--version", action="store_true", help="Mostrar versión de la herramienta")
    parser.add_argument("-o", "--output", metavar="FILE", help="Guardar correos encontrados en FILE.txt")
    parser.add_argument("--update", action="store_true", help="Actualizar herramienta")

    args = parser.parse_args()

    # 1) Version / Banner
    if args.version:
        print(f"Spatula: {__version__}")
        sys.exit(0)
    else:
        print(BANNER)

    # 2) Update
    if args.update:
        perform_update()
        sys.exit(0)

    # 3) Validar URL
    if not args.url or not args.url.startswith(('http://', 'https://')):
        print(f"❌  URL inválida: '{args.url}'")
        sys.exit(1)

    url = args.url.rstrip('/')
    scraper = None

    try:
        scraper = EmailScraper(
            base_url=args.url,
            max_depth=args.depth,
            headless=args.visible,
            max_pages=args.subdomains,
            page_timeout=args.timeout,
            delay=args.delay,
            hide=args.hide
        )
        scraper.run()
    except KeyboardInterrupt:
        print(f"\n{BRIGHT}{MAGENTA}Interrupcion por el usuario. Mostrando resultados parciales...\n{RESET}")
    except WebDriverException as e:
        print(f"{BRIGHT}{RED}Error en el navegador: {e}{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{BRIGHT}{RED}Error: {e}{RESET}")
        sys.exit(1)
    finally:
        if scraper:
            resultados = scraper.get_results()
            if resultados:
                if args.output:
                    with open(args.output, 'w', encoding="utf-8") as f:
                        for e in sorted(resultados):
                            f.write(e + '\n')
                    print(f"{BRIGHT}{GREEN}Correos guardados: {WHITE}{args.output}{RESET}")
                else:
                    print(f"\n{BRIGHT}{MAGENTA}Emails encontrados:{RESET}\n")
                    for email in sorted(resultados):
                        print(f"# {email}")
            else:
                print(f"❗ {RED}No se encontraron emails.\n{RESET}")
            try:
                scraper.close()
            except Exception as e:
                print(f"❗ {RED}Error al cerrar el navegador:{RESET} {e}")
            except KeyboardInterrupt:
                print(f"{BRIGHT}{YELLOW}\nSaliendo...{RESET}")
