# ADR-0004: Progreso de busqueda asincrono

- Fecha: 2026-04-22
- Estado: Aceptada

## Contexto

Procesar PDFs extensos puede tardar y una peticion sin respuesta visible hace
parecer que la aplicacion se detuvo.

## Decision

Ejecutar cada busqueda en un hilo de fondo y guardar su estado en memoria. La
interfaz inicia el trabajo mediante `POST /api/search` y consulta periodicamente
`GET /api/search/<job_id>` para actualizar porcentaje, pagina y mensaje.

## Consecuencias

- La interfaz informa avance real por pagina.
- Los trabajos se pierden si se reinicia la aplicacion, lo cual es aceptable
  para una herramienta local de una sola persona.
- No se incorpora una cola externa ni una base de datos.
