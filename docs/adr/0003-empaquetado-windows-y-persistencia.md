# ADR-0003: Empaquetado Windows y persistencia

- Fecha: 2026-04-21
- Actualizada: 2026-07-16
- Estado: Aceptada

## Contexto

La persona usuaria necesita iniciar la aplicacion desde un acceso directo sin
gestionar manualmente Python ni una consola. PyInstaller empaqueta la aplicacion,
pero sus archivos internos no son adecuados para datos persistentes.

## Decision

Generar `RelevamientoBORA.exe` con PyInstaller en modo `--onefile --windowed`.
Cuando corre empaquetada, conservar una copia de keywords en
`%LOCALAPPDATA%` o `%APPDATA%` bajo `BibliotecaCPAU/RelevamientoBORA`.

Desde 2026-07-16, las keywords empaquetadas son la fuente versionada y se
incorporan al archivo persistente sin eliminar terminos personalizados previos.

## Consecuencias

- El ejecutable puede abrirse sin ventana de consola.
- La aplicacion conserva configuracion entre builds.
- Cada build nuevo puede aportar keywords versionadas al archivo de usuario.
- Las eliminaciones o reemplazos de keywords requieren una migracion explicita;
  el merge automatico solo garantiza incorporaciones.
