# ADR-0005: Gestion controlada de keywords

- Fecha: 2026-07-16
- Estado: Aceptada

## Contexto

La edicion libre desde la interfaz puede introducir duplicados, patrones regex
demasiado amplios o cambios sin justificacion. Ademas, el detector nacional no
comparte estructura ni reglas con el proyecto del Boletin Oficial CABA.

## Decision

Retirar el editor de keywords de la interfaz. Gestionar incorporaciones mediante
el skill `gestionar-keywords-bora-nacional`, que opera exclusivamente sobre
`desktop_app/keywords.json` de este repositorio.

El skill debe revisar duplicados, cobertura por patrones existentes, necesidad
real de regex, validez del patron y pruebas positivas/negativas. Cada cambio se
registra en `docs/seguimiento/log_cambios.md`.

## Consecuencias

- La configuracion queda versionada y auditable.
- Agregar una keyword requiere una propuesta explicita y validacion previa.
- El skill `ajustar-keywords-bo-caba` no debe usarse en este proyecto.
- Los cambios de logica de clasificacion quedan fuera del skill y requieren una
  decision de arquitectura independiente.
