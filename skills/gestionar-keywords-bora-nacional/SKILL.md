---
name: gestionar-keywords-bora-nacional
description: >-
  Evaluar, agregar, validar y registrar keywords o patrones regex del buscador
  local del Boletin Oficial de la Republica Argentina. Use when Codex works in
  the relevamiento-boletin-oficial-argentina repository and the user asks to
  add a term, legal reference or spelling variant to desktop_app/keywords.json.
  Check duplicates and existing pattern coverage, decide whether regex is
  justified, require positive and negative examples, and append the change to
  docs/seguimiento/log_cambios.md. Never use for the Boletin Oficial CABA or
  the relevamiento_boletin_oficial_caba repository.
---

# Gestionar keywords BORA nacional

Mantener el listado nacional con cambios pequenos, verificables y trazables.
No aplicar las categorias ni las reglas del detector CABA: este proyecto usa
una lista unica en `desktop_app/keywords.json` y cada valor se compila como
expresion regular con `re.IGNORECASE`.

## Confirmar el proyecto

1. Leer `AGENTS.md` y ejecutar `git status --short`.
2. Confirmar que existen:
   - `desktop_app/keywords.json`;
   - `desktop_app/search_core.py`;
   - `docs/seguimiento/log_cambios.md`;
   - `docs/adr/0005-gestion-controlada-de-keywords.md`.
3. Detenerse si el repo contiene `config/config_keywords.json` o se llama
   `relevamiento_boletin_oficial_caba`. En ese caso corresponde el skill
   `ajustar-keywords-bo-caba`.

## Diagnosticar el candidato

1. Registrar el termino solicitado, el motivo bibliotecario y al menos un
   ejemplo real o representativo que deba detectarse.
2. Ejecutar, desde la raiz del repo:

```powershell
python skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py check --repo . --candidate "TERMINO"
```

3. Revisar:
   - coincidencia exacta sin distinguir mayusculas;
   - duplicado normalizado sin distinguir espacios ni tildes;
   - cobertura completa por un regex existente;
   - solapamiento parcial con patrones actuales;
   - validez sintactica del candidato como regex.
4. No agregar el candidato si ya existe o queda cubierto por un patron actual.

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

## Presentar la propuesta

Antes de editar, informar:

1. Termino solicitado y evidencia.
2. Resultado del control de duplicados y cobertura.
3. Valor exacto propuesto para el JSON.
4. Eleccion de literal o regex y su justificacion.
5. Casos positivos y negativos.
6. Riesgo de sobrecaptura.

Esperar aprobacion explicita del valor exacto cuando se proponga un regex o se
amplie el alcance del termino solicitado.

## Aplicar y registrar

Usar el script para modificar simultaneamente la configuracion y el log:

```powershell
python skills/gestionar-keywords-bora-nacional/scripts/manage_keyword.py add `
  --repo . `
  --value "VALOR_APROBADO" `
  --reason "MOTIVO" `
  --evidence "EVIDENCIA" `
  --positive "TEXTO_QUE_DEBE_COINCIDIR" `
  --negative "TEXTO_QUE_NO_DEBE_COINCIDIR"
```

El comando debe:

- rechazar duplicados y patrones invalidos;
- verificar todos los ejemplos positivos y negativos;
- agregar el valor sin reordenar entradas existentes;
- conservar UTF-8 y el formato `{"keywords": [...]}`;
- anexar una entrada a `docs/seguimiento/log_cambios.md`.

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
`docs/seguimiento/log_cambios.md`. Informar el valor agregado, las pruebas y
el riesgo residual. No hacer commit, push ni PR sin confirmacion explicita.

Para usar la nueva keyword desde codigo fuente, reiniciar `run_desktop.bat`.
Para el acceso directo, cerrar la aplicacion y regenerar el ejecutable con
`build_desktop_exe.bat`.
