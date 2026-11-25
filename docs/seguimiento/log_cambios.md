# Log de cambios

Registro cronologico y append-only de cambios funcionales, tecnicos y de
configuracion del proyecto. Las decisiones de arquitectura se desarrollan en
`docs/adr/` y se enlazan desde cada entrada cuando corresponde.

## 2025-05-14 a 2025-12-11 - Prototipo en Google Colab

- Tipo: evolucion funcional.
- Cambio: se desarrollo y ajusto el notebook de busqueda sobre PDFs del
  Boletin Oficial de la Republica Argentina.
- Origen: commits de la serie `Creado con Colab`.
- Validacion registrada: ejecucion iterativa en Colab; no consta una suite de
  pruebas automatizadas en esta etapa.
- ADR: no corresponde; etapa de prototipado anterior a la arquitectura activa.

## 2026-03-24 - Documentacion y separacion inicial de componentes

- Tipo: organizacion del repositorio.
- Cambio: se mejoro el README, se movio el notebook a `notebooks/` y se creo
  una separacion inicial para la aplicacion web.
- Origen: commits `cde7f1b`, `7f4f336` y `985de90`.
- Validacion registrada: revision de estructura y enlaces del README.
- ADR: antecedente de [ADR-0001](../adr/0001-aplicacion-local-como-version-activa.md).

## 2026-04-21 - Aplicacion local como version activa

- Tipo: cambio de arquitectura y despliegue.
- Cambio: se elimino la version activa de Hugging Face Spaces y se consolido
  una aplicacion local Flask con interfaz HTML y nucleo de busqueda separado.
- Origen: commit `959165e` e historial de implementacion del proyecto.
- Validacion registrada: carga de la ruta principal y ejecucion local.
- ADR: [ADR-0001](../adr/0001-aplicacion-local-como-version-activa.md) y
  [ADR-0002](../adr/0002-separacion-interfaz-y-nucleo-de-busqueda.md).

## 2026-04-21 - Empaquetado para Windows

- Tipo: distribucion local.
- Cambio: se agrego el build con PyInstaller, el ejecutable de una sola pieza,
  el icono personalizado y la persistencia de keywords en datos del usuario.
- Origen: commits `b3f8fd9` y `866af7f`.
- Validacion registrada: generacion de `dist/RelevamientoBORA.exe`.
- ADR: [ADR-0003](../adr/0003-empaquetado-windows-y-persistencia.md).

## 2026-04-22 - Progreso visible y ejecucion sin consola

- Tipo: experiencia de uso.
- Cambio: la busqueda paso a ejecutarse en segundo plano con consulta periodica
  de estado; el build se configuro como `--windowed` para ocultar la consola.
- Origen: commit `3f308f6`.
- Validacion registrada: flujo simulado hasta estado `completed` y build del
  ejecutable.
- ADR: [ADR-0004](../adr/0004-progreso-de-busqueda-asincrono.md).

## 2026-04-24 - Resultados consolidados y resaltados

- Tipo: mejora funcional.
- Cambio: se deduplicaron resultados por pagina, se agruparon las keywords
  detectadas y se resaltaron las coincidencias dentro del fragmento.
- Origen: commit `7b1196a`.
- Validacion registrada: pruebas sinteticas de multiples coincidencias,
  escape seguro de HTML y respuesta `200` de la ruta principal.
- ADR: no corresponde; no cambia los limites de la arquitectura.

## 2026-06-11 - Instrucciones de mantenimiento del proyecto

- Tipo: documentacion tecnica.
- Cambio: se agrego `AGENTS.md` con criterios de organizacion, calidad,
  verificacion y publicacion.
- Origen: commit `7be1953`.
- Validacion registrada: revision del archivo en el repositorio.
- ADR: no corresponde.

## 2026-07-16 - Trazabilidad, gestion de keywords y diseno operativo

- Tipo: gobernanza, configuracion e interfaz.
- Cambio: se adopto este log append-only y el registro de decisiones mediante
  ADRs; la edicion de keywords se retiro de la interfaz y se traslado al skill
  `gestionar-keywords-bora-nacional`; la interfaz se adecuo al sistema visual
  de interfaces operativas.
- Origen: decision de mantenimiento registrada en el hilo de implementacion.
- Validacion registrada: `compileall`, seis pruebas unitarias, validacion
  formal del skill, control de duplicados, carga Flask, revision visual en
  1280 y 360 px sin desbordamiento y build exitoso con PyInstaller.
- ADR: [ADR-0005](../adr/0005-gestion-controlada-de-keywords.md) y
  [ADR-0006](../adr/0006-sistema-visual-operativo.md).

## 2026-07-17 - Publicacion y proteccion de la rama principal

- Tipo: publicacion y gobernanza Git.
- Cambio: se integro el PR #1 en `main`, se eliminaron las ramas de trabajo
  local y remota y se alinearon las instrucciones de mantenimiento con el
  flujo adoptado. `main` permanece protegida y exige pull request, sin
  aprobaciones externas obligatorias; `force push` y eliminacion siguen
  bloqueados.
- Origen: [PR #1](https://github.com/Juan-Draghi/relevamiento-boletin-oficial-argentina/pull/1),
  commit de merge `f602d05` y decision de configuracion posterior al merge.
- Validacion registrada: PR en estado `MERGED`, ausencia de pull requests
  abiertos, unica rama local y remota `main`, y consulta de la proteccion de
  rama con `required_approving_review_count: 0`, `allow_force_pushes: false` y
  `allow_deletions: false`.
- ADR: no corresponde; es una decision operativa de mantenimiento del
  repositorio y no modifica la arquitectura de la aplicacion.

## 2026-11-14 - Migracion del asistente de desarrollo a Claude Code

- Tipo: configuracion del entorno de desarrollo y documentacion.
- Cambio: se agrego `CLAUDE.md`, que importa `AGENTS.md` para conservar una
  sola fuente de instrucciones; la skill `gestionar-keywords-bora-nacional` se
  movio de `skills/` a `.claude/skills/` para que Claude Code la detecte como
  skill de proyecto, y se actualizaron sus rutas, la de
  `tests/test_keyword_manager.py`, `AGENTS.md` y `README.md`. El prefijo de
  ramas de trabajo pasa de `codex/` a `claude/`. Las skills globales usadas
  con Codex se copiaron a la carpeta de usuario de Claude Code, fuera del
  repositorio.
- Origen: decision de la persona usuaria de gestionar el proyecto con Claude
  Code en lugar de Codex.
- Validacion registrada: `python -m compileall desktop_app`,
  `python -m unittest discover -s tests`, comando `check` de la skill desde su
  nueva ruta y `git diff --check`.
- ADR: no corresponde; no modifica la arquitectura de la aplicacion. El
  ADR-0006 se conserva sin cambios: la skill `disenar-interfaces-operativas`
  sigue siendo la referencia, ahora disponible como skill global de Claude Code.

## 2026-11-17 - Interfaz con la marca Biblioteca CPAU

- Tipo: cambio de interfaz y decision de arquitectura.
- Cambio: la interfaz pasa del sistema visual neutro al kit de la skill
  `cpau-estilo` con la marca Biblioteca CPAU. Se agregaron
  `desktop_app/static/cpau-app.css` (copia sin modificar del kit), `logo.png`
  (logo oficial) y `favicon.ico`; `styles.css` quedo reducido a los
  componentes propios de la app y `templates/index.html` usa las clases del
  kit. Los textos de la plantilla incorporan tildes y "keywords" se muestra
  como "palabras clave". Se conservaron endpoints, IDs y flujo de busqueda.
  `biblioteca-logo.png` queda sin uso en la carpeta `static`. Se actualizaron
  `AGENTS.md` y `README.md`.
- Origen: pedido de la persona usuaria de aplicar el estilo CPAU a la
  interfaz, con la decision explicita de reemplazar el ADR-0006.
- Validacion registrada: `python -m compileall desktop_app`; instancia de
  prueba en el puerto 7871 (el 7861 estaba en uso por otra instancia);
  Playwright a 1366 y 390 px con busqueda por URL del Boletin Oficial
  (finalizada, sin coincidencias ese dia) y con un PDF local de prueba (2
  paginas con coincidencias); cambio de origen URL/archivo; sin desplazamiento
  horizontal y sin errores de consola. No se regenero el ejecutable.
- ADR: [ADR-0007](../adr/0007-marca-biblioteca-cpau-en-la-interfaz.md), que
  reemplaza al [ADR-0006](../adr/0006-sistema-visual-operativo.md).

## 2026-11-17 - Regeneracion del ejecutable con la marca Biblioteca CPAU

- Tipo: empaquetado.
- Cambio: se regenero `dist\RelevamientoBORA.exe` con PyInstaller 6.19.0 y
  los mismos parametros de `build_desktop_exe.bat`, para incorporar la
  interfaz descripta en la entrada anterior. El ejecutable previo se conservo
  como `dist\RelevamientoBORA_anterior-2026-07-17.exe`.
- Origen: la persona usuaria seguia viendo la interfaz anterior porque usaba
  el ejecutable empaquetado en julio, que incluye su propia copia de
  plantillas y estilos.
- Validacion registrada: listado del contenido empaquetado (`cpau-app.css`,
  `logo.png`, `favicon.ico`, `styles.css`, `index.html`) y ejecucion del
  `.exe` en el puerto 7861 con la interfaz nueva; las keywords sincronizadas
  en los datos del usuario se siguieron cargando (38).
- ADR: [ADR-0007](../adr/0007-marca-biblioteca-cpau-en-la-interfaz.md).

## 2026-11-17 - Script para detener la aplicacion local

- Tipo: cambio funcional de ejecucion.
- Cambio: se agrego `stop_desktop.bat`, que cierra todo proceso que escuche en
  el puerto 7861 (codigo fuente o `RelevamientoBORA.exe`), con el mismo
  mecanismo que la app del BO CABA (`netstat` + `taskkill`).
  `run_desktop.bat` lo invoca antes de iniciar, para no duplicar instancias.
  Se actualizo `README.md`.
- Origen: la app seguia activa al cerrar la pestaña y se acumulaban copias del
  ejecutable en el puerto 7861 (se detectaron dos). La persona usuaria eligio
  replicar el esquema de scripts de la app del BO CABA.
- Validacion registrada: copia del script con el puerto 7871; dos instancias
  de prueba en ese puerto quedaron cerradas y las instancias del puerto 7861
  no se modificaron. No se ejecuto sobre el puerto 7861 para no cerrar las
  copias abiertas por la persona usuaria.
- ADR: no corresponde; no modifica la arquitectura ni los limites entre
  componentes.

## 2026-11-17 - Eliminacion del logo sin uso

- Tipo: limpieza de recursos.
- Cambio: se elimino `desktop_app/static/biblioteca-logo.png`, que quedo sin
  referencias al adoptar el logo oficial `logo.png` del kit CPAU.
- Origen: pedido de la persona usuaria.
- Validacion registrada: busqueda de referencias a `biblioteca-logo` en el
  codigo, plantillas, scripts y documentacion vigente (solo la mencionan
  entradas historicas del log); `python -m compileall desktop_app`. El
  ejecutable actual todavia lo incluye; se quita en el proximo build. La copia
  de resguardo `dist\RelevamientoBORA_anterior-2026-07-17.exe`, no versionada,
  se envio a la Papelera de reciclaje.
- ADR: no corresponde.

## 2026-11-17 - Altas, modificaciones y bajas en el skill de keywords

- Tipo: cambio de procedimiento y herramienta de mantenimiento.
- Cambio: el skill `gestionar-keywords-bora-nacional` paso de admitir solo
  altas a admitir altas, modificaciones y bajas. `manage_keyword.py` suma los
  subcomandos `list` (ubicar el valor exacto), `replace` (reemplazo en la
  misma posicion, con control de duplicados contra el resto de la lista) y
  `remove` (verifica que los ejemplos negativos dejen de detectarse y que los
  positivos sigan detectandose por otras keywords). `SKILL.md` incorpora una
  ficha de cambio con aprobacion explicita del valor exacto, segun el modelo
  del skill del BO CABA pero sin comparacion contra registros historicos, ya
  que esta aplicacion no los guarda. Se actualizaron `README.md` y
  `agents/openai.yaml`.
- Origen: pedido de la persona usuaria.
- Validacion registrada: `python -m unittest discover -s tests` (7 pruebas
  nuevas para reemplazo, baja y rechazos); `list` y un `remove` con valor
  inexistente ejecutados sobre el repo sin modificar
  `desktop_app/keywords.json`.
- ADR: no corresponde; amplia el procedimiento previsto en ADR-0005.

## 2026-11-17 - Sincronizacion de bajas y reemplazos en el ejecutable

- Tipo: cambio tecnico de persistencia.
- Cambio: `desktop_app/app.py` reemplaza `merge_keywords` por
  `sync_keywords`. Al iniciar el ejecutable, la copia de
  `%LOCALAPPDATA%\BibliotecaCPAU\RelevamientoBORA\keywords.json` se
  reconstruye con las keywords del build mas los terminos personales, y la
  lista del build se guarda en `keywords_build.json`. Asi, las bajas y
  reemplazos hechos con el skill llegan al ejecutable al regenerarlo. Se
  actualizaron `SKILL.md`, `README.md` y ADR-0003.
- Origen: al ampliar el skill a bajas y modificaciones se detecto que el
  ejecutable solo agregaba keywords nuevas a su copia. La persona usuaria
  pidio aplicar la mejora en la app.
- Validacion registrada: `python -m unittest discover -s tests` (3 pruebas
  nuevas: primer arranque, baja/reemplazo con termino personal y escritura de
  ambos archivos con rutas temporales); comparacion de solo lectura de la
  copia real con el repositorio (38 frente a 37; el termino propio es un
  patron para el Decreto 1017, que se conservaria).
- ADR: [ADR-0008](../adr/0008-sincronizacion-de-keywords-del-ejecutable.md).

## 2026-11-17 - Ajuste de keywords BORA nacional

- Tipo: configuracion de busqueda.
- Cambio: se reemplazo `decreto 1017/2024` por `[Dd]ecreto(?: (?:N[°º]|n[°º])\.?)? ?1017(?:/?(?:2024|24))?` en `desktop_app/keywords.json` (posicion 18).
- Motivo: Incorporar al repositorio el patron del Decreto 1017/2024 que solo existia en la copia del ejecutable, para cubrir citas con N°/Nº y ano completo o abreviado, con el mismo formato que los demas decretos de la lista.
- Evidencia: Patron presente como termino personal en la copia del ejecutable (%LOCALAPPDATA%); identificacion de la norma aportada por la persona usuaria. Riesgo aceptado: tambien detecta 'Decreto 1017/2023' y 'Decreto 10170/2024', como los demas decretos de la lista.
- Validacion: 5 caso(s) positivo(s) y 2 caso(s) negativo(s) superados con el valor nuevo; regex compilado.
- ADR: no corresponde; se aplica ADR-0005.

## 2026-11-17 - Build que cierra y reabre la aplicacion

- Tipo: cambio funcional de empaquetado.
- Cambio: `build_desktop_exe.bat` ahora llama a `stop_desktop.bat` antes de
  compilar, quita la marca de solo lectura de
  `build\RelevamientoBORA\localpycs` si existe y, al terminar bien, abre
  `dist\RelevamientoBORA.exe` y cierra la ventana sin pausa. Ante un error
  conserva la pausa con el mensaje. Se actualizo `README.md`.
- Origen: el build fallo con `PermissionError` porque OneDrive dejo esa
  carpeta temporal como solo lectura, y el `.exe` abierto impedia
  reemplazarlo. La persona usuaria pidio evitar cerrar y abrir la app a mano
  en cada regeneracion.
- Validacion registrada: ejecucion completa del `.bat` con la app abierta: la
  cerro, genero el ejecutable (09:37:49) y lo abrio (09:37:53), con una sola
  instancia escuchando en el puerto 7861.
- ADR: no corresponde; no modifica la arquitectura ni ADR-0003.

## 2026-11-25 - Ajuste de keywords BORA nacional

- Tipo: configuracion de busqueda.
- Cambio: se agrego `NAG[- –]?201(?!\d)` a `desktop_app/keywords.json`.
- Motivo: Incorporar la norma tecnica NAG-201 pedida por la persona usuaria, cubriendo variantes de separador (guion, espacio, sin separador, guion largo) que aparecen al extraer texto de PDFs.
- Evidencia: Pedido de la persona usuaria; ejemplo representativo 'Apruébase la Norma NAG-201' (sin ejemplar real del Boletin Oficial). Se uso (?!\d) para no detectar NAG-2010.
- Validacion: 5 caso(s) positivo(s) y 2 caso(s) negativo(s) superados; regex compilado.
- ADR: no corresponde; se aplica ADR-0005.

## 2026-11-25 - Ajuste de keywords BORA nacional

- Tipo: configuracion de busqueda.
- Cambio: se agrego `NAG[- –]?200(?!\d)` a `desktop_app/keywords.json`.
- Motivo: Incorporar la norma nacional NAG-200 (disposiciones y normas minimas para la ejecucion de instalaciones domiciliarias de gas, GN-GL), complementaria de NAG-201 (instalaciones industriales de gas; version 2026, ya cubierta por su keyword). Mismo patron que NAG-201 para cubrir variantes de separador.
- Evidencia: Pedido y descripcion de la norma aportados por la persona usuaria; ejemplo representativo 'Norma NAG-200 (GN-GL)' (sin ejemplar real del Boletin Oficial). Se uso (?!\d) para no detectar NAG-2000.
- Validacion: 4 caso(s) positivo(s) y 2 caso(s) negativo(s) superados; regex compilado.
- ADR: no corresponde; se aplica ADR-0005.
