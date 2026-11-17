# ADR-0007: Marca Biblioteca CPAU en la interfaz

- Fecha: 2026-11-17
- Estado: Aceptada
- Reemplaza a: [ADR-0006](0006-sistema-visual-operativo.md)

## Contexto

El ADR-0006 adopto un sistema visual neutro, sin marca institucional, definido
por la skill `disenar-interfaces-operativas`. La persona usuaria decidio pasar
la interfaz a la imagen de la Biblioteca CPAU, definida por la skill
`cpau-estilo` para aplicaciones locales.

## Decision

Usar el kit de interfaz de `cpau-estilo` con la marca Biblioteca CPAU:

- `desktop_app/static/cpau-app.css`: copia sin modificar del kit
  (`assets/app/cpau-app.css`). Se actualiza copiando de nuevo el archivo de la
  skill, no editandolo.
- `desktop_app/static/styles.css`: solo los componentes propios de esta app
  (cabecera con indicador, progreso y registros de resultados), construidos
  con las variables del kit.
- `logo.png` (logo oficial `biblioteca-color.png`) y `favicon.ico` del kit.
- Barra superior con logo y nombre de la app, Roboto, fondo #f7f6f5,
  superficies blancas y azul #3400ff solo para la accion principal, la
  seleccion y los indicadores. Estetica plana y solo modo claro.

Se mantienen sin cambios los endpoints, los IDs que usa el JavaScript de
progreso, el flujo de busqueda y los resultados como registros apilados. No se
agregan dependencias, CDNs ni fuentes remotas. El icono del ejecutable
(`app-icon.ico`) no cambia.

## Consecuencias

- La interfaz es consistente con las demas herramientas de la Biblioteca CPAU.
- Los cambios de interfaz siguen `cpau-estilo` (`references/aplicaciones.md`)
  y ya no `disenar-interfaces-operativas`.
- Cada cambio de interfaz debe verificarse a 1366 y 390 px, sin desplazamiento
  horizontal y sin errores de consola.
- Si la skill actualiza el kit, hay que volver a copiar `cpau-app.css` y
  revisar `styles.css`.
