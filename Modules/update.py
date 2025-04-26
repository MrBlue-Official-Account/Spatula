"""
    # Selenium update tool
"""
# pylint: disable=C0301,C0116,W0718

import os
import sys
import re
import shutil
import tempfile
import subprocess
import requests

from Modules.banner import BRIGHT, GREEN, RED, YELLOW, WHITE,RESET

__version__ = '1.2.0'

RAW_UPDATE_URL = "https://raw.githubusercontent.com/MrBlue-Official-Account/Spatula/main/Modules/update.py"

def get_local_version():
    try:
        here = os.path.dirname(__file__)
        local_file = os.path.join(here, 'update.py')
        with open(local_file, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", line)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"‼️ {BRIGHT}{RED}Error al leer la version local:{RESET} {e}")
        sys.exit(1)

def get_remote_version():
    try:
        response = requests.get(RAW_UPDATE_URL, timeout=15)
        response.raise_for_status()
        for line in response.text.splitlines():
            match = re.match(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", line)
            if match:
                return match.group(1)
        print(f"⚠️ {BRIGHT}{YELLOW}Advertencia:{RESET} No se encontro la version en el archivo remoto.")
        return None
    except requests.RequestException as e:
        print(f"❌ {BRIGHT}{RED}Error al obtener la version remota:{RESET} {e}")
        sys.exit(1)

def parse_version(version_str):
    return tuple(map(int, version_str.strip().split('.')))

def perform_update():
    local_version = get_local_version()
    remote_version = get_remote_version()

    if not remote_version:
        print(f"❗️ {BRIGHT}{YELLOW}No se pudo determinar la version remota. Abortando actualizacion.{RESET}")
        return

    print(f"{BRIGHT}{WHITE}version local:{RESET}{GREEN} {local_version}")
    print(f"{BRIGHT}{WHITE}version remota:{RESET}{GREEN} {remote_version}")

    if parse_version(remote_version) > parse_version(local_version):
        print(f"{BRIGHT}{GREEN}Nueva version disponible. Actualizando...{RESET}")
        try:
            temp_dir = tempfile.mkdtemp()
            subprocess.check_call(['git', 'clone', 'https://github.com/MrBlue-Official-Account/Spatula.git', temp_dir])

            current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

            for item in os.listdir(temp_dir):
                src_path = os.path.join(temp_dir, item)
                dst_path = os.path.join(current_dir, item)

                if os.path.exists(dst_path):
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)

                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

            print(f"{BRIGHT}{GREEN}actualizacion completada exitosamente a la version {remote_version}.{RESET}")

        except subprocess.CalledProcessError as e:
            print(f"❌ {BRIGHT}{RED}Error al clonar el repositorio:{RESET} {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ {BRIGHT}{RED}Error durante la actualizacion:{RESET} {e}")
            sys.exit(1)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        print(f"{BRIGHT}{YELLOW}Ya estás en la version mas reciente ({local_version}).{RESET}")


if __name__ == '__main__':
    perform_update()
