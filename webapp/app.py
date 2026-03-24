import io
import json
import re
import html
from typing import Optional

import pdfplumber
import requests
import gradio as gr

KEYWORDS_FILE = "keywords.json"
# URL por defecto: primera sección del día
DEFAULT_URL = "https://s3.arsat.com.ar/cdn-bo-001/pdf-del-dia/primera.pdf"


def load_keywords():
    """Carga la lista de keywords desde el archivo JSON."""
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("keywords", [])
    return data


def build_html_table(resultados):
    """Arma una tabla HTML; encabezados visibles y columnas ajustadas al contenido."""
    if not resultados:
        return ""

    filas = []
    for r in resultados:
        kw = html.escape(str(r["Keyword hallada"]))
        pagina = html.escape(str(r["Número de página"]))
        frag = html.escape(str(r["Fragmento de texto"]))
        filas.append(
            f"<tr>"
            f"<td>{kw}</td>"
            f"<td style='text-align:center;'>{pagina}</td>"
            f"<td class='fragment-cell'>{frag}</td>"
            f"</tr>"
        )

    tabla_html = """
    <style>
    .results-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: auto;
    }
    .results-table th,
    .results-table td {
        border: 1px solid #444;
        padding: 8px;
        vertical-align: top;
        font-size: 0.9rem;
    }
    /* Encabezados: fondo gris claro y texto negro, forzado sobre el theme */
    .results-table th {
        background-color: #f0f0f0 !important;
        color: #000 !important;
        font-weight: bold;
        text-align: left;
    }
    /* Columna de keyword: lo más angosta posible */
    .results-table th:nth-child(1),
    .results-table td:nth-child(1) {
        white-space: nowrap;
        width: 1%;
    }
    /* Columna de página: muy angosta y centrada */
    .results-table th:nth-child(2),
    .results-table td:nth-child(2) {
        white-space: nowrap;
        width: 1%;
        text-align: center;
    }
    /* Fragmento: ocupa el resto del ancho y hace wrap */
    .results-table td.fragment-cell {
        white-space: normal;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    </style>
    <table class="results-table">
      <thead>
        <tr>
          <th>Keyword hallada</th>
          <th>Número de página</th>
          <th>Fragmento de texto</th>
        </tr>
      </thead>
      <tbody>
    """ + "\n".join(filas) + """
      </tbody>
    </table>
    """
    return tabla_html


def buscar_normativa(url_pdf: str, pdf_bytes: Optional[bytes]):
    """
    Si se sube un PDF, se usa ese archivo.
    Si no se sube, se usa la URL (por defecto o la que se indique).
    Se usa un indicador de progreso textual en vez de la barra flotante.
    """

    if not url_pdf:
        url_pdf = DEFAULT_URL

    # 1) Obtener el contenido del PDF
    if pdf_bytes:
        pdf_content = pdf_bytes
        # mensaje inicial
        yield "Se recibió un archivo PDF, comenzando el análisis...", ""
    else:
        yield "Descargando PDF desde la URL...", ""
        try:
            resp = requests.get(url_pdf)
            resp.raise_for_status()
            pdf_content = resp.content
        except Exception as e:
            yield f"Error al descargar el PDF: {e}", ""
            return

    # 2) Cargar keywords desde JSON
    try:
        keywords = load_keywords()
    except FileNotFoundError:
        yield "No se encontró el archivo keywords.json en el Space.", ""
        return
    except Exception as e:
        yield f"Error al leer keywords.json: {e}", ""
        return

    resultados = []

    # 3) Procesar PDF y buscar coincidencias
    try:
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            num_pages = len(pdf.pages)
            if num_pages == 0:
                yield "El PDF no contiene páginas legibles.", ""
                return

            for page_index, page in enumerate(pdf.pages):
                # Progreso textual
                yield f"Analizando página {page_index + 1} de {num_pages}...", ""
                text = page.extract_text()
                if not text:
                    continue

                for term in keywords:
                    # Intentar compilar como regex; si falla, usar búsqueda literal
                    try:
                        pattern = re.compile(term, re.IGNORECASE)
                    except re.error:
                        pattern = re.compile(re.escape(term), re.IGNORECASE)

                    for m in pattern.finditer(text):
                        start = max(m.start() - 200, 0)
                        end = m.end() + 200
                        contexto = text[start:end].replace("\n", " ").strip()

                        resultados.append(
                            {
                                "Keyword hallada": term,
                                "Número de página": page_index + 1,
                                "Fragmento de texto": contexto,
                            }
                        )
    except Exception as e:
        yield f"Error al procesar el PDF: {e}", ""
        return

    # 4) Mensaje + tabla HTML final
    if not resultados:
        mensaje = "No se detectó normativa relevante"
        tabla_html = ""
    else:
        mensaje = f"Se hallaron {len(resultados)} normas relevantes"
        tabla_html = build_html_table(resultados)

    yield mensaje, tabla_html


with gr.Blocks() as demo:
    # CSS general para mejorar la altura de la caja de URL
    gr.HTML(
        """
        <style>
        /* Aumenta la altura de la caja de texto de la URL */
        #url_input textarea, 
        #url_input input {
            min-height: 3rem !important;
            padding-top: 0.6rem !important;
            padding-bottom: 0.6rem !important;
            font-size: 0.95rem !important;
        }
        </style>
        """
    )

    gr.Markdown(
        "# Búsqueda de normativa relevante en el Boletín Oficial de la República Argentina"
    )

    with gr.Row():
        url_input = gr.Textbox(
            label="URL del ejemplar del Boletín Oficial (PDF)",
            value=DEFAULT_URL,
            lines=1,
            placeholder="Si no cambiás nada, se usa la URL por defecto del día",
            elem_id="url_input",
        )
        archivo_input = gr.File(
            label="Subí un ejemplar en PDF (opcional)",
            file_types=[".pdf"],
            type="binary",
        )

    buscar_btn = gr.Button("Buscar normativa relevante")

    mensaje_output = gr.Markdown()
    tabla_output = gr.HTML(label="Resultados")

    buscar_btn.click(
        fn=buscar_normativa,
        inputs=[url_input, archivo_input],
        outputs=[mensaje_output, tabla_output],
    )


if __name__ == "__main__":
    demo.launch()