# Busqueda de normativa en el Boletin Oficial de la República Argentina

[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)
[![Repositorio GitHub](https://img.shields.io/badge/GitHub-Repositorio-black)](https://github.com/Juan-Draghi/relevamiento-boletin-oficial-argentina)

Aplicacion local para relevar normativa publicada en el Boletin Oficial de la
Republica Argentina mediante palabras clave y expresiones regulares sobre
documentos PDF.

La version activa es la aplicacion local con interfaz HTML. El notebook de
Colab se conserva solamente como antecedente.

## Acceso rapido

- Aplicacion local: [`desktop_app/`](desktop_app/)
- Instalacion: [`install_desktop.bat`](install_desktop.bat)
- Ejecucion: [`run_desktop.bat`](run_desktop.bat)
- Build del ejecutable: [`build_desktop_exe.bat`](build_desktop_exe.bat)
- Log de cambios: [`docs/seguimiento/log_cambios.md`](docs/seguimiento/log_cambios.md)
- Decisiones de arquitectura: [`docs/adr/`](docs/adr/)
- Skill de keywords: [`skills/gestionar-keywords-bora-nacional/`](skills/gestionar-keywords-bora-nacional/)

## Que hace la herramienta

- Lee ejemplares del Boletin Oficial en PDF.
- Acepta una URL o un archivo PDF local.
- Busca terminos y expresiones regulares.
- Informa el progreso real por pagina.
- Devuelve una sola entrada por pagina con todas las keywords detectadas.
- Resalta las coincidencias dentro de cada fragmento.

## Requisitos previos

- Windows.
- Python 3 instalado y disponible en `PATH` para ejecutar desde codigo fuente.
- Conexion a Internet solamente cuando se usa una URL remota.

Las dependencias de ejecucion estan en `desktop_app/requirements.txt`.

## Como usar

1. Ejecutar `install_desktop.bat` una vez.
2. Ejecutar `run_desktop.bat`.
3. La aplicacion abrira `http://127.0.0.1:7861` en el navegador.
4. Elegir `URL` o `Archivo local`.
5. Iniciar la busqueda y revisar las paginas detectadas.

Cerrar la pestaña del navegador no detiene el proceso local. Para regenerar el
ejecutable, cerrar primero todas las instancias de `RelevamientoBORA.exe`.

## Gestionar keywords

La interfaz no permite editar keywords. La fuente versionada es
`desktop_app/keywords.json` y los cambios deben realizarse con el skill
`gestionar-keywords-bora-nacional`.

Ejemplo de invocacion:

```text
Use $gestionar-keywords-bora-nacional para evaluar y agregar la keyword "termino" al BORA nacional.
```

El skill:

- verifica duplicados y cobertura por patrones existentes;
- determina si corresponde usar un literal o un regex acotado;
- exige casos positivos y negativos;
- valida el JSON y el patron;
- registra el cambio en `docs/seguimiento/log_cambios.md`.

No usar para este proyecto el skill `ajustar-keywords-bo-caba`: el detector
CABA tiene otro repositorio, otro esquema de configuracion y otras reglas.

Cuando la aplicacion corre empaquetada, conserva las keywords del usuario en:

```text
%LOCALAPPDATA%\BibliotecaCPAU\RelevamientoBORA\keywords.json
```

Al iniciar un build nuevo, agrega al archivo persistente las keywords
versionadas que aun no existan, sin borrar terminos personalizados anteriores.

## Generar el ejecutable

1. Cerrar todas las instancias de `RelevamientoBORA.exe`.
2. Ejecutar `build_desktop_exe.bat`.
3. Usar el archivo generado en `dist/RelevamientoBORA.exe`.

El build usa PyInstaller en modo `--onefile --windowed`.

## Trazabilidad

Los cambios funcionales, tecnicos y de configuracion se agregan de forma
cronologica a `docs/seguimiento/log_cambios.md`.

Las decisiones que afectan arquitectura, limites o forma de operacion se
documentan como ADR en `docs/adr/`. El indice y los estados estan en
`docs/adr/README.md`.

## Estructura principal

```text
.
|-- desktop_app/
|   |-- app.py
|   |-- keywords.json
|   |-- search_core.py
|   |-- requirements.txt
|   |-- build_requirements.txt
|   |-- static/
|   `-- templates/
|-- docs/
|   |-- adr/
|   `-- seguimiento/
|-- skills/
|   `-- gestionar-keywords-bora-nacional/
|-- tests/
|-- notebooks/
|-- build_desktop_exe.bat
|-- install_desktop.bat
|-- run_desktop.bat
`-- README.md
```

## Organizacion del codigo

- `desktop_app/search_core.py`: descarga, lectura de PDF, matching y resultados.
- `desktop_app/app.py`: Flask, API local, progreso y persistencia.
- `desktop_app/templates/index.html`: interfaz operativa.
- `desktop_app/static/`: estilos, logo e icono.
- `skills/gestionar-keywords-bora-nacional/`: procedimiento auditable de
  mantenimiento de keywords.
- `notebooks/`: prototipo historico de Google Colab.

## Pruebas

```powershell
python -m compileall desktop_app
python -m unittest discover -s tests
```

Para verificar el empaquetado:

```powershell
cmd /c build_desktop_exe.bat
```

## Tecnologias

- Python
- Flask
- HTML, CSS y JavaScript nativos
- pdfplumber
- requests
- PyInstaller

## Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE).

## Autor

Juan Draghi  
Biblioteca del Consejo Profesional de Arquitectura y Urbanismo  
Con asistencia de ChatGPT
