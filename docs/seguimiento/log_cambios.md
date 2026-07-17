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
