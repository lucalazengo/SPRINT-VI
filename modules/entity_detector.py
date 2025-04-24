# modules/entity_detector.py
import re
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from modules.llm_assist import query_llm, is_ollama_running


MODEL_NAME = "celiudos/legal-bert-lgpd"

regex_patterns = {
    "CPF": r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
    "CNPJ": r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "TELEFONE": r"\+?\d{0,3}[\s-]?\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}",
    "CEP": r"\b\d{5}-?\d{3}\b",
    "DINHEIRO": r"R\$[\s]?[0-9\.,]+",
    "URL": r"\bhttps?://[^\s]+|www\.[^\s]+",
    "ENDERECO": r"\b(rua|avenida|travessa|alameda|rodovia)[^\n]+?\d{1,5}\b"
}


def get_ner_pipeline():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
    return pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="first", device=0 if torch.cuda.is_available() else -1)

def detect_with_regex(text):
    entities = []
    for label, pattern in regex_patterns.items():
        for match in re.finditer(pattern, text):
            entities.append({"start": match.start(), "end": match.end(), "label": label})
    return entities

def detect_with_ner(text, ner_pipeline):
    ner_results = ner_pipeline(text)
    return [{"start": r["start"], "end": r["end"], "label": r["entity_group"]} for r in ner_results]

def merge_entities(text, regex_entities, ner_entities):
    all_entities = regex_entities + ner_entities
    # Remove sobreposição
    all_entities.sort(key=lambda e: e["start"])
    filtered = []
    last_end = -1
    for ent in all_entities:
        if ent["start"] > last_end:
            filtered.append(ent)
            last_end = ent["end"]
    return filtered

def detect_sensitive_entities(text, ner_pipeline, restrict=True):
    # 1. Detectar entidades por regex
    regex_entities = detect_with_regex(text)

    # 2. Detectar entidades contextuais por NER
    ner_entities = detect_with_ner(text, ner_pipeline)

    # 3. Unir e filtrar sobreposições
    all_entities = merge_entities(text, regex_entities, ner_entities)

    # 4. Otimizar com validação via LLM (opcional)
    if is_ollama_running() and restrict:
        filtered = []
        for ent in all_entities:
            if ent["label"].upper() in ["NOME", "ENDERECO", "DATA", "DINHEIRO"]:
                if validate_with_llm(text, ent):
                    filtered.append(ent)
            else:
                filtered.append(ent)
        return filtered
    else:
        return all_entities


def anonymize_entities(text, entities, mask="***"):
    """
    Anonimiza entidades sensíveis no texto.
    """
    if not entities:
        return text
    offset = 0
    for entity in entities:
        start = entity["start"] + offset
        end = entity["end"] + offset
        text = text[:start] + mask + text[end:]
        offset += len(mask) - (end - start)
    return text

def validate_with_llm(text, entity, mask_type="***"):
    context = text[max(0, entity['start'] - 50):entity['end'] + 50]
    entity_text = text[entity['start']:entity['end']]
    
    prompt = f"""
Você é um assistente de proteção de dados com base na LGPD.

A seguinte frase contém uma entidade sensível:

"{context}"

Texto destacado: "{entity_text}"

Este texto destacado é um dado pessoal ou sensível segundo a LGPD? Responda apenas com SIM ou NÃO.
"""
    response = query_llm(prompt)
    return "SIM" in response.upper()

