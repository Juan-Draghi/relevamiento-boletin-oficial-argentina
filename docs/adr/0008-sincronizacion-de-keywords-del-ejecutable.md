# ADR-0008: Sincronizacion de keywords del ejecutable

- Fecha: 2026-11-17
- Estado: Aceptada
- Modifica: [ADR-0003](0003-empaquetado-windows-y-persistencia.md), en lo
  relativo a la incorporacion de keywords al archivo persistente.

## Contexto

El ejecutable usa una copia persistente de keywords en
`%LOCALAPPDATA%\BibliotecaCPAU\RelevamientoBORA\keywords.json`. Segun
ADR-0003, al iniciar solo se le agregaban las keywords nuevas del build. Al
ampliarse el skill `gestionar-keywords-bora-nacional` a modificaciones y
bajas, ese criterio dejaba activos en el ejecutable los valores eliminados o
reemplazados en el repositorio.

La copia puede contener terminos personales cargados cuando la interfaz
permitia editar keywords (antes de ADR-0005). En la copia de la Biblioteca se
verifico al menos uno (un patron para el Decreto 1017) que no figura en el
repositorio.

## Decision

Al iniciar el ejecutable:

1. Leer las keywords del build, la copia persistente y `keywords_build.json`
   (lista del build sincronizado la vez anterior, en la misma carpeta).
2. Reconstruir la copia como: keywords del build, en su orden, mas los
   terminos personales, es decir, los de la copia que no figuran ni en el
   build anterior ni en el actual (comparacion sin distinguir mayusculas).
3. Guardar la lista del build actual en `keywords_build.json`.

Si `keywords_build.json` no existe (primer arranque con este mecanismo), todo
termino de la copia que no este en el build se conserva como personal.

La logica vive en `desktop_app/app.py` (`sync_keywords` y
`ensure_keywords_file`), porque es coordinacion de la persistencia del
ejecutable y no procesamiento de PDF. Desde codigo fuente no cambia nada: se
usa directamente `desktop_app/keywords.json`.

## Consecuencias

- Altas, modificaciones y bajas versionadas llegan al ejecutable al
  regenerarlo, sin pasos manuales.
- Se conservan los terminos personales existentes.
- En el primer arranque con este mecanismo, un valor eliminado en ese mismo
  build se conserva como personal; desde el build siguiente las bajas se
  propagan.
- El orden de la copia pasa a ser el del build, seguido de los personales.
- La copia persistente no debe editarse a mano para quitar valores del
  build: se restaurarian en el siguiente arranque.
