# Relevamiento del Boletin Oficial de la Republica Argentina

[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Juan-Draghi/relevamiento-boletin-oficial-argentina/blob/main/notebooks/Busqueda_Boletin_Oficial_RA_v3.ipynb)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-yellow)](https://huggingface.co/spaces/J-Draghi/relevamiento_bora)
[![Repositorio GitHub](https://img.shields.io/badge/GitHub-Repositorio-black)](https://github.com/Juan-Draghi/relevamiento-boletin-oficial-argentina)

Herramienta para relevar normativa publicada en el Boletin Oficial de la Republica Argentina mediante busquedas por palabras clave y patrones dentro de documentos PDF.

Este repositorio conserva el origen y la evolucion del proyecto:

1. Prototipo inicial desarrollado en Google Colab.
2. Adaptacion posterior como aplicacion web.
3. Despliegue publico en Hugging Face Spaces.

## Acceso rapido

- App web: [Relevamiento Bora en Hugging Face Spaces](https://huggingface.co/spaces/J-Draghi/relevamiento_bora)
- Repositorio: [Juan-Draghi/relevamiento-boletin-oficial-argentina](https://github.com/Juan-Draghi/relevamiento-boletin-oficial-argentina)
- Notebook original: [Busqueda_Boletin_Oficial_RA_v3.ipynb](https://github.com/Juan-Draghi/relevamiento-boletin-oficial-argentina/blob/main/notebooks/Busqueda_Boletin_Oficial_RA_v3.ipynb)
- Abrir en Colab: [Google Colab](https://colab.research.google.com/github/Juan-Draghi/relevamiento-boletin-oficial-argentina/blob/main/notebooks/Busqueda_Boletin_Oficial_RA_v3.ipynb)
- Carpeta para la app web: [`webapp/`](webapp/)


## Que hace la herramienta

- Lee ejemplares del Boletin Oficial en PDF.
- Busca terminos exactos y expresiones regulares.
- Detecta menciones relevantes dentro del texto.
- Facilita la revision de normativa de interes profesional.
- Permite exportar resultados para su analisis posterior.

## Evolucion del proyecto

La primera version fue desarrollada como notebook en Google Colab para experimentar rapido con el procesamiento de PDFs, ajustar palabras clave y exportar resultados sin requerir instalacion local.

Mas adelante, ese prototipo se transformo en una aplicacion web para simplificar el acceso desde navegador y hacer la herramienta mas util para usuarios no tecnicos. La version publicada se encuentra en Hugging Face Spaces.

Frase breve sugerida para describir el proyecto en GitHub:

> Prototipo original en Google Colab, posteriormente adaptado como aplicacion web y desplegado en Hugging Face Spaces.

## Como usar

### Opcion 1: usar la app web

1. Abrir el Space en Hugging Face.
2. Ingresar la URL de un PDF del Boletin Oficial o cargar un archivo PDF.
3. Ejecutar la busqueda.
4. Revisar los resultados obtenidos.

### Opcion 2: usar el notebook original

1. Abrir `notebooks/Busqueda_Boletin_Oficial_RA_v3.ipynb`.
2. Ejecutar las celdas en Google Colab o en Jupyter.
3. Ajustar las palabras clave si hace falta.
4. Exportar y revisar los resultados.


## Tecnologias y despliegue

- Prototipo inicial: Google Colab / Jupyter Notebook
- Version web publicada: Hugging Face Spaces
- Interfaz del Space: Gradio
- Lenguaje principal: Python

## Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE).

## Autor

Juan Draghi  
Biblioteca del Consejo Profesional de Arquitectura y Urbanismo  
Con asistencia de ChatGPT
