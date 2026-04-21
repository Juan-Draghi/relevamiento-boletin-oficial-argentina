# Busqueda de normativa en el Boletin Oficial de la Republica Argentina

[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)
[![Repositorio GitHub](https://img.shields.io/badge/GitHub-Repositorio-black)](https://github.com/Juan-Draghi/relevamiento-boletin-oficial-argentina)

Aplicacion local para relevar normativa publicada en el Boletin Oficial de la Republica Argentina mediante busquedas por palabras clave y expresiones regulares sobre documentos PDF.

El repositorio queda orientado a una sola version activa del proyecto: la aplicacion de escritorio/local con interfaz HTML.

## Acceso rapido

- Aplicacion local: [`desktop_app/`](desktop_app/)
- Script de instalacion: [`install_desktop.bat`](install_desktop.bat)
- Script de ejecucion: [`run_desktop.bat`](run_desktop.bat)

## Que hace la herramienta

- Lee ejemplares del Boletin Oficial en PDF.
- Acepta una URL de PDF o un archivo local cargado desde la PC.
- Busca terminos exactos y expresiones regulares.
- Devuelve coincidencias con numero de pagina y fragmento contextual.
- Permite editar y guardar el listado de keywords desde la propia interfaz HTML.

## Como usar

1. Ejecutar `install_desktop.bat` una vez para instalar dependencias.
2. Ejecutar `run_desktop.bat`.
3. Se abrira la interfaz local en el navegador.
4. Ingresar la URL de un PDF o subir un PDF desde la PC.
5. Ejecutar la busqueda y revisar los resultados.
6. Si hace falta, desplegar el editor de keywords y actualizar el listado.

La aplicacion corre localmente en `http://127.0.0.1:7861`.

## Antecedente

El notebook original de Google Colab se conserva en [`notebooks/Busqueda_Boletin_Oficial_RA_v3.ipynb`](notebooks/Busqueda_Boletin_Oficial_RA_v3.ipynb) solo como antecedente de prototipado.

## Estructura del repositorio

```text
.
|-- desktop_app/
|   |-- app.py
|   |-- keywords.json
|   |-- requirements.txt
|   |-- search_core.py
|   |-- static/
|   |   |-- biblioteca-logo.png
|   |   `-- styles.css
|   `-- templates/
|       `-- index.html
|-- notebooks/
|   `-- Busqueda_Boletin_Oficial_RA_v3.ipynb
|-- install_desktop.bat
|-- LICENSE
|-- run_desktop.bat
`-- README.md
```

## Organizacion del codigo

- `desktop_app/app.py` contiene la aplicacion Flask local.
- `desktop_app/search_core.py` contiene la logica de descarga, lectura de PDF y busqueda.
- `desktop_app/keywords.json` guarda el listado editable de keywords.
- `desktop_app/templates/index.html` define la interfaz HTML.
- `desktop_app/static/` contiene estilos y assets visuales.
- `notebooks/` conserva el prototipo original en Colab.

## Tecnologias

- Python
- Flask
- HTML y CSS
- pdfplumber
- requests

## Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE).

## Autor

Juan Draghi  
Biblioteca del Consejo Profesional de Arquitectura y Urbanismo  
Con asistencia de ChatGPT
