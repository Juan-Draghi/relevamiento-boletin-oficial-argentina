---
name: gestionar-keywords-bora-nacional
description: >-
  Evaluar, agregar, modificar, eliminar, validar y registrar keywords o
  patrones regex del buscador local del Boletin Oficial de la Republica
  Argentina. Use when working in the relevamiento-boletin-oficial-argentina
  repository and the user asks to add, edit, replace, correct, narrow, widen
  or remove a term, legal reference or spelling variant in
  desktop_app/keywords.json, or to list the current keywords. Check
  duplicates and existing pattern coverage, decide whether regex is
  justified, require positive and negative examples, get explicit approval
  of the exact change and append it to docs/seguimiento/log_cambios.md.
  Never use for the Boletin Oficial CABA or the
  relevamiento_boletin_oficial_caba repository.
---

# Gestionar keywords BORA nacional

Mantener el listado nacional con cambios pequenos, verificables y trazables.
No aplicar las categorias ni las reglas del detector CABA: este proyecto usa
una lista unica en `desktop_app/keywords.json` y cada valor se compila como
expresion regular con `re.IGNORECASE`.

La aplicacion no guarda resultados de busquedas anteriores. Por eso no hay
comparacion contra registros historicos: la evidencia son los ejemplos
(positivos y negativos) y los casos que aporta la persona usuaria.

Operaciones admitidas:

| Operacion | Subcomando | Cuando |
|---|---|---|
| Alta | `add` | Falta un termino o una variante. |
| Modificacion | `replace` | Corregir, acotar o ampliar un valor existente. |
| Baja | `remove` | Falso positivo sistematico, termino obsoleto o redundante. |

Todos los comandos se ejecutan desde la raiz del repo con:

```powershell
python .claude/skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py <subcomando> --repo . ...
```

## Confirmar el proyecto

1. Leer las instrucciones del proyecto (`AGENTS.md`, incorporado por
   `CLAUDE.md`) y ejecutar `git status --short`.
2. Confirmar que existen:
   - `desktop_app/keywords.json`;
   - `desktop_app/search_core.py`;
   - `docs/seguimiento/log_cambios.md`;
   - `docs/adr/0005-gestion-controlada-de-keywords.md`.
3. Detenerse si el repo contiene `config/config_keywords.json` o se llama
   `relevamiento_boletin_oficial_caba`. En ese caso corresponde el skill
   `ajustar-keywords-bo-caba`.
4. Si `desktop_app/keywords.json` tiene cambios sin registrar en el log,
   detenerse e informar antes de operar.

## Reunir la evidencia

Para cualquier operacion, registrar:

- termino o valor afectado;
- motivo bibliotecario (omision, falso positivo, error de escritura, termino
  obsoleto, redundancia);
- al menos un ejemplo real o representativo: sumario, fragmento de norma o
  ejemplar del Boletin Oficial.

Si falta evidencia esencial, pedirla antes de proponer. No agregar ni quitar
terminos solo porque parezcan relacionados tematicamente.

## Ubicar el valor actual (modificacion y baja)

Las operaciones `replace` y `remove` exigen el valor exacto del JSON. Ubicarlo
con:

```powershell
python .claude/skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py list --repo . --contains "texto"
```

El filtro ignora mayusculas y tildes. Si la persona usuaria nombra un concepto
cubierto por varios valores, mostrarlos y pedir que elija.

## Diagnosticar el valor nuevo (alta y modificacion)

```powershell
python .claude/skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py check --repo . --candidate "TERMINO"
```

Revisar:

- coincidencia exacta sin distinguir mayusculas;
- duplicado normalizado sin distinguir espacios ni tildes;
- cobertura completa por un regex existente;
- solapamiento parcial con patrones actuales;
- validez sintactica del candidato como regex.

No agregar el candidato si ya existe o queda cubierto. En una modificacion,
el `check` muestra al valor actual como duplicado o solapado: es esperable,
porque `replace` compara el valor nuevo contra el resto de la lista.

## Decidir literal o regex

Preferir un termino literal cuando la forma textual sea estable. Recordar que
la aplicacion compila todos los valores como regex: escapar `.` `(` `)` `+`
`?` y otros metacaracteres cuando deban buscarse literalmente.

Usar regex solo si existe una variacion concreta que deba cubrirse, por ejemplo:

- tildes u ortografias documentadas;
- numero de norma con separadores o ano abreviado;
- abreviaturas o componentes opcionales acotados.

Mantener los patrones estrechos:

- usar grupos no capturantes `(?:...)`;
- evitar `.*`, comodines abiertos y raices demasiado generales;
- no volver opcional el concepto principal;
- aprovechar `re.IGNORECASE` en vez de duplicar mayusculas y minusculas;
- definir al menos un caso positivo y uno negativo.

## Evaluar una baja

Antes de proponer una baja, determinar que se pierde:

- **Falso positivo:** el ejemplo que molesta debe dejar de detectarse. Se
  pasa como `--negative`; el script falla si otra keyword lo sigue captando.
  Considerar primero si conviene acotar el valor con `replace` en lugar de
  eliminarlo.
- **Redundancia u obsolescencia:** los textos relevantes deben seguir
  detectandose por otras keywords. Se pasan como `--positive`; el script
  falla si alguno deja de detectarse.

Cada baja necesita al menos un ejemplo de alguno de los dos tipos. Informar
siempre que perdida de cobertura se acepta: una baja reduce resultados y no
hay historico para medir cuantos.

## Presentar la ficha de cambio

Antes de editar, informar:

1. **Operacion:** alta, modificacion o baja.
2. **Evidencia y motivo.**
3. **Valor actual** (modificacion y baja) y **valor propuesto** (alta y
   modificacion), exactos como quedaran en el JSON.
4. **Diagnostico:** resultado de `check` o de `list`.
5. **Literal o regex** y su justificacion.
6. **Casos positivos y negativos.**
7. **Riesgo:** sobrecaptura (alta, ampliacion) o perdida de cobertura (baja,
   acotamiento).

Esperar aprobacion explicita de la ficha. Toda baja y toda modificacion
requieren aprobacion del valor exacto; en un alta, tambien cuando se proponga
un regex o se amplie el alcance del termino pedido. Una autorizacion generica
anterior no sustituye esa aprobacion.

## Aplicar y registrar

Cada subcomando valida, modifica `desktop_app/keywords.json` sin reordenar el
resto de las entradas, conserva UTF-8 y el formato `{"keywords": [...]}` y
anexa una entrada a `docs/seguimiento/log_cambios.md`. Si una validacion
falla, no modifica nada.

Alta:

```powershell
python .claude/skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py add `
  --repo . `
  --value "VALOR_APROBADO" `
  --reason "MOTIVO" `
  --evidence "EVIDENCIA" `
  --positive "TEXTO_QUE_DEBE_COINCIDIR" `
  --negative "TEXTO_QUE_NO_DEBE_COINCIDIR"
```

Modificacion (el valor nuevo ocupa la misma posicion que el anterior):

```powershell
python .claude/skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py replace `
  --repo . `
  --current "VALOR_ACTUAL_EXACTO" `
  --value "VALOR_NUEVO_APROBADO" `
  --reason "MOTIVO" `
  --evidence "EVIDENCIA" `
  --positive "TEXTO_QUE_EL_VALOR_NUEVO_DEBE_DETECTAR" `
  --negative "TEXTO_QUE_EL_VALOR_NUEVO_NO_DEBE_DETECTAR"
```

Baja:

```powershell
python .claude/skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py remove `
  --repo . `
  --value "VALOR_ACTUAL_EXACTO" `
  --reason "MOTIVO" `
  --evidence "EVIDENCIA" `
  --negative "TEXTO_QUE_DEBE_DEJAR_DE_DETECTARSE" `
  --positive "TEXTO_QUE_DEBE_SEGUIR_DETECTANDOSE"
```

`--positive` y `--negative` pueden repetirse. En `remove` son opcionales por
separado, pero debe haber al menos uno.

### Copia del ejecutable

El ejecutable usa una copia persistente en
`%LOCALAPPDATA%\BibliotecaCPAU\RelevamientoBORA\keywords.json`. Al iniciar,
la reconstruye con las keywords del build mas los terminos personales que no
vinieron en ningun build, y guarda la lista del build en
`keywords_build.json` (ADR-0008). Por eso altas, modificaciones y bajas llegan
solas al ejecutable despues de regenerarlo; no editar esa copia a mano.

Limite: la primera vez que arranca un build con este mecanismo no hay lista
anterior, asi que un valor eliminado en ese mismo build se conserva como
personal. Si ocurre, repetir la baja despues de ese primer arranque o
avisarlo en el cierre.

No editar `desktop_app/app.py` ni `desktop_app/search_core.py`. Si el caso exige
cambiar logica, detenerse y explicar que requiere desarrollo y posiblemente un
ADR, no un ajuste de keywords.

## Validar y cerrar

Ejecutar:

```powershell
python -m json.tool desktop_app/keywords.json > $null
python -m unittest discover -s tests
git diff --check
git status --short
```

Revisar el diff de `desktop_app/keywords.json` y
`docs/seguimiento/log_cambios.md`. Si una validacion posterior falla, revertir
ambos archivos con `git checkout --` (es seguro porque se confirmo que no
tenian cambios previos) e informar. No dejar la configuracion modificada sin
su registro.

Informar la operacion, el valor anterior y el nuevo, las pruebas, el estado de
la copia del ejecutable y el riesgo residual. No hacer commit, push ni PR sin
confirmacion explicita.

Para usar el cambio desde codigo fuente, reiniciar con `stop_desktop.bat` y
`run_desktop.bat`. Para el acceso directo, cerrar la aplicacion y regenerar el
ejecutable con `build_desktop_exe.bat`.
