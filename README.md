# Relevamiento diario del Boletín Oficial de la República Argentina

Este repositorio contiene un script desarrollado en Python (Google Colab) para automatizar la búsqueda diaria de normativa vinculada al ejercicio profesional de la arquitectura en los ejemplares del Boletín Oficial de la República Argentina.

## Objetivo

Facilitar la detección de disposiciones, resoluciones, leyes, decretos y otra normativa urbanística o edilicia mediante la búsqueda automatizada de términos clave y expresiones regulares en el PDF diario del Boletín.

## Características

- Lectura de texto desde archivos PDF del Boletín Oficial.
- Búsqueda de términos exactos y expresiones regulares.
- Posibilidad de definir palabras clave desde una lista o un archivo Excel.
- Exportación de resultados a un archivo `.xlsx` con los términos encontrados y su contexto.
- Interfaz ejecutable desde Google Colab, sin necesidad de instalación local.

## Requisitos

- Cuenta de Google para utilizar Google Colab.
- Archivo PDF del Boletín Oficial descargado localmente.
- (Opcional) Archivo `.xlsx` con palabras clave personalizadas.

## Instrucciones de uso

1. Abrir el notebook en Google Colab.
2. Subir el archivo PDF del Boletín del día.
3. Subir el archivo de términos clave (o editar la lista manualmente en el código).
4. Ejecutar las celdas del notebook.
5. Descargar el archivo de resultados (`resultados_busqueda_BORA.xlsx`).

## Licencia

Este proyecto está disponible bajo la [Licencia MIT](LICENSE).  
Se permite su uso, copia, modificación y redistribución con o sin fines comerciales, siempre que se mantenga la atribución correspondiente.


## Autor:
Juan Draghi — Biblioteca del Consejo Profesional de Arquitectura y Urbanismo (con la asistencia de ChatGPT)
