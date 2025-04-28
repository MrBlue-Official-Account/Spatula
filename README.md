<p align="right"><img src="https://img.shields.io/badge/STATUS-EN%20DESAROLLO-green"></p>

## Spatula
 
Diseñado en la extracción de correos, mediante la navegación web. Utilizando Selenium como paquete base y Chromedriver  para simular la actividad de un usuario sin disparar los métodos anti-scraping empleados por las webs.
## Funciones

- *Ignorar certificados **SSL/TLS** inválidos de forma segura para evitar bloqueos por errores de seguridad.*
- *Personalizar tiempos de espera (timeouts) y retardos entre solicitudes para evitar la detección como bot*
- *Instalación automatizada: `-up`, `--update` & `-upd`,  `--update-drivers`*



>[!NOTE] Chromedriver
>Antes de iniciar cualquier escaneo, instalar el Chromedriver.*(**Linux** o **Windows**), ejecutando: 
>```sh
>python3 spatula.py -upd
>```

## Instalación

```sh
git clone https://github.com/MrBlue-Official-Account/Spatula.git && cd Spatula && pip3 install -r requirements.txt
```

## Uso

Ejecutar el script principal con la URL objetivo:
```sh
python3 spatula.py https://springfield.edu/
```

![[Captura de pantalla 2025-04-28 075912.png]]


## Opciones Disponibles

>[!IMPORT]  Importante❗️
>Si ejecutará la herramienta en **Git Bash** desde Windows y salta por error: # [UnicodeEncodeError: 'charmap' codec can't encode characters](https://stackoverflow.com/questions/27092833/unicodeencodeerror-charmap-codec-cant-encode-characters) Ocurre, porque utiliza de forma predeterminada la codificación cp1252, que no puede representar algunos **Caracteres Unicode** en el banner o en la salida del programa.
>
>Ejecute el siguiente comando para evitar errores.
>```sh
 >PYTHONIOENCODING=utf-8 python3 spatula.py -h
>```
>![[2025-04-28_11-13.png]]


```powershell
python3 spatula.py -h
              _____
        ╔═╗┌─┐|\|/|┬ ┬┬  ┌─┐
        ╚═╗├─┘ |@| │ ││  ├─┤
        ╚═╝┴   |_| └─┘┴─┘┴ ┴
            \ v.1.2.0 /

usage: spatula.py [-h] [-d DEPTH] [-sb SUBDOMAINS] [-t TIMEOUT] [--delay DELAY] [-v] [-hd] [--version] [-o FILE] [-up] [-upd] [url]

Herramienta de scraping de correos electrónicos.

positional arguments:
  url                      URL base a explorar (por ejemplo: https://example.com)

options:
  -h, --help               show this help message and exit
  -d DEPTH, --depth DEPTH  Profundidad máxima de rastreo (por defecto: 2)
  -sb SUBDOMAINS, --subdomains SUBDOMAINS
                           Número máximo de páginas a visitar (0 = ilimitado)
  -t TIMEOUT, --timeout TIMEOUT
                           Timeout de carga de página (segundos)
  --delay DELAY            Retraso entre peticiones (segundos)
  -v, --visible            Mostrar navegador (modo visible)
  -hd, --hide              Ocultar los enlaces durante la navegación
  --version                Mostrar versión de la herramienta
  -o FILE, --output FILE   Guardar correos encontrados en FILE.txt

UPDATE:
  -up, --update            Actualizar herramienta
  -upd, --update-drivers   Actualizar Chromedriver para Win y Linux
```

- `-d`, `--depth`
	- *Profundidad máxima de rastreo en árbol de enlaces.*
		```sh
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -d 20 
		```

- `-sb`, `--subdomains`
	- *Número máximo de páginas a visitar (0 = ilimitado)*
		```sh
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -sb 280
		```

- `-t`, `--timeout`
	- *Tiempo de espera para la carga de cada página (en segundos)*
		```
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -sb 280 -t 20 --delay 2
		```

- `--delay` 
	- *Retardo entre solicitudes (en segundos)*
		```
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -sb 280 -t 20 --delay 2
		```

- `-v`, `--visible`
	- *Mostrar el navegador durante el scraping.*
		```
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -sb 280 -t 20 --delay 2
		```

- `-hd`, `--hide`
	- *Ocultar los enlaces que se van procesando en la salida.*
		```
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -sb 280 -t 20 --delay 2
		```

- `-o`, `--output`
	- *Guardar los correos en el fichero `FILE.txt`*
		```
		python3 spatula.py http://repositoriodigital.fundacite-merida.gob.ve/ -sb 280 -t 20 --delay 2
		```

#### 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres mejorar Spatula, por favor:

1. *Haz un fork de este repositorio.*
   
2. *Crea una rama* (`git checkout -b feature/nombre-de-tu-función`).
   
3. *Realiza tus cambios y añade tests si procede.*
   
4. *Envía un **pull request** describiendo tu propuesta.*

#### ⚠️ Acotaciones

- Esta herramienta está en **versión 1.2.0** y sigue en desarrollo.
   
- Puede haber cambios sin previo aviso; detalla en tu PR cualquier ruptura de compatibilidad.
   
- Para discusiones más amplias, usa el canal de _**Issues**_ del repositorio.

## 📧 Contacto

Si detectas un fallo crítico o tienes una sugerencia, puedes escriba al **Hellopt_APK@proton.me**
