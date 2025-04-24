# modules/document_builder.py

import pandas as pd
from fpdf import FPDF
from odf.opendocument import OpenDocumentText
from odf.text import P
from io import BytesIO
import tempfile

def rebuild(file, text, ext):
    if ext == "pdf":
        return rebuild_pdf(text)
    elif ext == "odt":
        return rebuild_odt(text)
    elif ext == "csv":
        return rebuild_csv(text)
    else:
        return text.encode("utf-8")

def rebuild_pdf(text):
    from fpdf import FPDF
    import re

    def sanitize(text_line):
        # remove ou substitui caracteres que o fpdf não consegue renderizar (ex: box drawing, símbolos especiais)
        return re.sub(r'[^\x00-\x7F]+', '', text_line)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        line = sanitize(line)
        pdf.multi_cell(0, 10, line)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf.output(tmp.name)
        tmp.seek(0)
        return tmp.read()


def rebuild_odt(text):
    doc = OpenDocumentText()
    for line in text.split("\n"):
        p = P(text=line)
        doc.text.addElement(p)

    with tempfile.NamedTemporaryFile(suffix=".odt", delete=False) as tmp:
        doc.save(tmp.name)
        tmp.seek(0)
        return tmp.read()

def rebuild_csv(text):
    from io import StringIO
    df = pd.read_csv(StringIO(text))
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()
