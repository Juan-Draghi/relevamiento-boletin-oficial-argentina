# ADR-0002: Separacion entre interfaz y nucleo de busqueda

- Fecha: 2026-04-21
- Estado: Aceptada

## Contexto

La lectura del PDF, la compilacion de patrones y el armado de resultados son
reglas reutilizables. Mezclarlas con rutas Flask y renderizado HTML dificulta
las pruebas y el mantenimiento.

## Decision

Separar el sistema en dos capas principales:

- `desktop_app/search_core.py`: descarga, extraccion, matching y resultados.
- `desktop_app/app.py`: coordinacion, API local, progreso y presentacion.

La plantilla y los estilos permanecen en `templates/` y `static/`.

## Consecuencias

- La logica de PDF puede probarse sin iniciar Flask.
- Los cambios visuales no deben duplicar reglas de busqueda.
- Las rutas y contratos JSON deben mantenerse estables al redisenar la UI.
