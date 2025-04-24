from flask import Blueprint, render_template, request, send_file, redirect, flash
from modules import file_handler, text_extractor, entity_detector, anonymizer, document_builder
import time
import os

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            uploaded_file = request.files.get("documento")
            texto_manual = request.form.get("texto_manual")
            mask = request.form.get("mask_type", "***")
            usar_llm = bool(request.form.get("usar_llm"))
            agressivo = bool(request.form.get("agressivo"))
            formato_saida = request.form.get("formato_saida", "pdf").lower()

            if not uploaded_file and not texto_manual:
                flash("Envie um arquivo ou cole um texto.")
                return redirect("/")

            ext = uploaded_file.filename.split(".")[-1].lower() if uploaded_file else "txt"
            content = uploaded_file.read() if uploaded_file else texto_manual.encode()

            inicio = time.time()

            texto = text_extractor.extract_text(content, ext)
            pipeline = entity_detector.get_ner_pipeline()
            entidades = entity_detector.detect_sensitive_entities(texto, pipeline, restrict=not agressivo)
            texto_anon = anonymizer.anonymize_text(texto, entidades, mask=mask)
            texto_anon = anonymizer.extra_pass_cleaning(texto_anon, mask=mask, aggressive=agressivo)

            if usar_llm:
                texto_anon = anonymizer.contains_sensitive_semantics(texto_anon, mask=mask)

            saida_ext = ext if formato_saida == "mesmo" else formato_saida
            nome_saida = f"anonimizado_{int(time.time())}.{saida_ext}"
            log_path = os.path.join("logs", nome_saida)

            with open(log_path, "wb") as f:
                f.write(document_builder.rebuild(None, texto_anon, saida_ext))

            with open("logs/preview.txt", "w", encoding="utf-8") as p:
                p.write(texto_anon)

            tempo = round(time.time() - inicio, 2)
            return render_template(
                "resultado.html",
                nome_saida=nome_saida,
                tempo=tempo,
                preview=texto_anon
            )

        except Exception as e:
            erro = str(e)
            return render_template("erro.html", erro=erro)

    return render_template("index.html")

@main.route("/download/<path:filename>")
def download_file(filename):
    log_path = os.path.join("logs", filename)
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=True)
    else:
        return f"Arquivo {filename} não encontrado.", 404
