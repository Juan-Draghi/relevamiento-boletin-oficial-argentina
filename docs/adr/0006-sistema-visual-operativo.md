# ADR-0006: Sistema visual operativo

- Fecha: 2026-07-16
- Estado: Aceptada

## Contexto

La aplicacion es una herramienta de trabajo repetitivo. La interfaz anterior
tenia una composicion mas institucional/editorial y una tabla poco adecuada
para fragmentos de longitud variable.

## Decision

Adoptar el sistema definido por el skill `disenar-interfaces-operativas`:
superficie clara sobre lienzo gris, tipografia de sistema, accion primaria azul
marino, densidad controlada, foco visible y componentes responsive.

Mostrar resultados como registros apilados con pagina, keywords y fragmento,
en lugar de una tabla ancha. Mantener sin cambios los endpoints y los IDs que
usa el JavaScript de progreso.

## Consecuencias

- La tarea principal aparece en el primer viewport y la ayuda secundaria se
  reduce.
- Los fragmentos extensos se adaptan mejor a pantallas angostas.
- No se agregan frameworks, fuentes ni iconos externos.
- Cada cambio futuro de interfaz debe validar teclado, estados y anchos de 1280,
  980, 720 y 360 px.
