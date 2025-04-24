# modules/text_extractor.py
import fitz  # PyMuPDF
import pandas as pd
from odf.opendocument import load
from odf.text import P

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    return text

def extract_text_from_odt(file_bytes):
    doc = load(BytesIO(file_bytes))
    paragraphs = doc.getElementsByType(P)
    text = "\n".join([str(p.firstChild.data) if p.firstChild else "" for p in paragraphs])
    return text

def extract_text_from_csv(file_bytes):
    df = pd.read_csv(BytesIO(file_bytes))
    return df.to_csv(index=False)

def extract_text(file_bytes, ext):
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "odt":
        return extract_text_from_odt(file_bytes)
    elif ext == "csv":
        return extract_text_from_csv(file_bytes)
    else:
        return file_bytes.decode("utf-8")
