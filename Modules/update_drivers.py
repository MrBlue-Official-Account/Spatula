"""
    # Selenium update drivers
"""
# pylint: disable=C0301,C0116,W0718
import os
import re
import sys
import shutil
import zipfile
import tempfile
import subprocess
import platform
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Directorios donde guarda actualmente los drivers
WIN_DIR   = Path(__file__).parent.parent / "chromedriver-win"
LINUX_DIR = Path(__file__).parent.parent / "chromedriver-linux"

# URL de la página de Chrome.
CHROME_TEST_URL = "https://googlechromelabs.github.io/chrome-for-testing/"

def get_local_version(driver_path: Path) -> str:
    """Ejecuta `<driver> -v` y extrae la versión (e.g. 'x.x.x.x')."""
    try:
        out = subprocess.check_output([str(driver_path), "-v"], stderr=subprocess.STDOUT, text=True)
        m = re.search(r"ChromeDriver\s+([\d\.]+)", out)
        return m.group(1) if m else ""
    except Exception:
        return ""

def parse_remote() -> (str, dict):
    """
    Descargar y parsear la página de Chrome.
    Devuelve:
        - remote_version: versión estable (string)
        - urls: dict plataforma → URL de zip
    """
    resp = requests.get(CHROME_TEST_URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    stable_sec = soup.find("section", id="stable")
    remote_version = stable_sec.find("p").find("code").get_text(strip=True)

    urls = {}
    table = stable_sec.find("div", class_="table-wrapper").find("tbody")
    for tr in table.find_all("tr", class_="status-ok"):
        binary = tr.find_all("th")[0].code.get_text(strip=True)
        plat   = tr.find_all("th")[1].code.get_text(strip=True)
        url_zip= tr.find_all("td")[0].code.get_text(strip=True)
        if binary == "chromedriver" and plat in ("linux64", "win32", "win64"):
            urls[plat] = url_zip

    return remote_version, urls

def download_and_replace(plat: str, url: str, dest_dir: Path):
    """Descargar, descomprimir y mover el binario a dest_dir, renombrando el de Win32."""
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / f"{plat}.zip"
        # Descargar
        with requests.get(url, stream=True, timeout=(5, 10)) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(1024*32):
                    f.write(chunk)
        # Descomprimir
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmp)
        exe_name = "chromedriver.exe" if plat.startswith("win") else "chromedriver"
        src = None
        for root, _, files in os.walk(tmp):
            if exe_name in files:
                src = Path(root) / exe_name
                break
        if not src:
            raise FileNotFoundError(f"‼️ No se encontro {exe_name} en el ZIP de {plat}")

        dest_dir.mkdir(parents=True, exist_ok=True)
        if plat == "win32":
            dst = dest_dir / "chromedriver32.exe"
        elif plat == "win64":
            dst = dest_dir / "chromedriver.exe"
        else:
            dst = dest_dir / "chromedriver"

        if dst.exists():
            dst.unlink()
        shutil.copy2(src, dst)
        if plat == "linux64":
            dst.chmod(0o755)

def update_all_drivers():
    os_name = platform.system().lower()
    # Determinar plataformas y crear sólo la carpeta correspondiente
    if os_name == "windows":
        arch = platform.machine().lower()
        if arch in ('i386','i686','x86'):
            plats = ["win32"]
        elif arch in ('amd64','x86_64','arm64'):
            plats = ["win64"]
        else:
            print(f"⚠️ Arquitectura Windows desconocida: {arch}")
            return
        WIN_DIR.mkdir(parents=True, exist_ok=True)
    elif os_name == "linux":
        plats = ["linux64"]
        LINUX_DIR.mkdir(parents=True, exist_ok=True)
    else:
        print(f"‼️ SO no soportado para update_drivers: {os_name}")
        return

    remote_ver, urls = parse_remote()
    print(f"\nVersion remota estable de ChromeDriver: {remote_ver}")

    for plat in plats:
        folder = WIN_DIR if plat.startswith("win") else LINUX_DIR
        if plat == "linux64":
            driver_path = folder / "chromedriver"
        elif plat == "win32":
            driver_path = folder / "chromedriver32.exe"
        else:
            driver_path = folder / "chromedriver.exe"

        local_ver = get_local_version(driver_path)
        print(f"[{plat}] Local: {local_ver or 'no instalado'}")

        if not local_ver or tuple(map(int, remote_ver.split('.'))) > tuple(map(int, local_ver.split('.'))):
            print(f" → Actualizando {plat} …")
            download_and_replace(plat, urls[plat], folder)
            print(f"    ✔ {plat} actualizado a {remote_ver}")
        else:
            print(f"    – {plat} ya esta en {local_ver}")

if __name__ == "__main__":
    try:
        update_all_drivers()
    except Exception as e:
        print(f"❌ Error en update_drivers: {e}", file=sys.stderr)
        sys.exit(1)
