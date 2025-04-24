# modules/anonymizer.py

import re
from textwrap import wrap
from modules.llm_assist import query_llm, is_ollama_running

def anonymize_text(text: str, entities: list, mask: str = "***") -> str:
    """
    Substitui entidades detectadas no texto pelo marcador definido.
    """
    anonymized = text
    for ent in sorted(entities, key=lambda e: e["start"], reverse=True):
        anonymized = anonymized[:ent["start"]] + mask + anonymized[ent["end"]:]
    return anonymized

def extra_pass_cleaning(text: str, mask: str = "***", aggressive: bool = True) -> str:
    """
    Etapa adicional de limpeza textual para capturar padrões residuais.
    O modo não agressivo evita sobreanônimos perigosos.
    """
    cleanup_patterns = [
        r"\bhttps?://[^\s]+",                                # URLs
        r"\bwww\.[^\s]+",                                    # domínios
        r"R\$[\s]?[0-9\.,]+",                                # valores monetários
        r"\b\d{1,3}(?:\.\d{1,3}){3}\b",                       # IPs
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", # e-mails
        r"\+?\d{0,3}[\s-]?\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}",    # telefones
        r"\b\d{5}-?\d{3}\b",                                 # CEPs
        r"\b(Rua|Av|Avenida|Travessa|Rodovia)\s+[^\n]+\d+",  # endereços com número
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",                       # datas com "/"
        r"\b[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9]{2,4}\b",          # datas com "."
        r"\b(religião|opinião política|orientação sexual|cor|etnia|raça|convicção)\s+[^\n]+"
    ]

    if aggressive:
        cleanup_patterns.append(
            r"\b(?:cem|mil|milhão|milhões|milhares|reais|centavos)\b"
        )

    for pattern in cleanup_patterns:
        text = re.sub(pattern, mask, text, flags=re.IGNORECASE)

    return text

def contains_sensitive_semantics(text: str, mask: str = "***", chunk_size: int = 600) -> str:
    """
    Divide o texto em blocos e verifica se contém informações sensíveis
      alinhado a definição da LGPD (Lei nº 13.709/2018).
    """
    if not is_ollama_running():
        return text

    chunks = wrap(text, chunk_size)
    anon_parts = []

    for chunk in chunks:
        prompt = f"""
Você é um assistente jurídico treinado na Lei Geral de Proteção de Dados (LGPD - Lei n.º 13.709/2018).

Sua tarefa é identificar e anonimizar dados pessoais e sensíveis contidos no texto abaixo, conforme os princípios da LGPD brasileira.

---

**DADOS PESSOAIS**: qualquer informação que permita identificar uma pessoa natural ou empresa, direta ou indiretamente.

Exemplos: nome completo,nome da empresa, data e local de nascimento, RG, CPF, endereço, telefone, e-mail, IP, cookies, hábitos de consumo, número de cartão bancário, dados de localização.

---

**DADOS SENSÍVEIS**: informações sobre origem racial ou étnica, convicções religiosas ou filosóficas, opiniões políticas, filiação sindical, dados genéticos, biométricos, sobre saúde ou vida sexual.

---

**INSTRUÇÕES**:
1. Substitua todos os dados pessoais e sensíveis por "{mask}".
2. Preserve o máximo possível da estrutura e sentido do texto original.
3. Não modifique trechos que não contenham dados protegidos.
4. Se houver dúvida, aja com cautela e substitua.

Texto:
{chunk}

Retorne **somente o texto anonimizado**, sem explicações adicionais.
"""
        result = query_llm(prompt)
        if result and not result.startswith("[ERRO"):
            anon_parts.append(result.strip())
        else:
            anon_parts.append(chunk)  # fallback em caso de erro

    return "\n".join(anon_parts)
