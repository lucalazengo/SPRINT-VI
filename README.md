# Anonimizador LGPD 

Esta é uma aplicação web desenvolvida com **Flask** e containerizada com **Docker**, voltada à **anonimização automática de documentos** conforme a **Lei Geral de Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018)**.

Ela permite que usuários jurídicos, técnicos ou analistas removam dados sensíveis de documentos carregados, preservando a estrutura textual e gerando arquivos prontos para uso seguro e público.

---

## Funcionalidades

-  Upload de arquivos: `.pdf`, `.odt`, `.csv` ou entrada manual de texto.
-  Detecção de dados pessoais e sensíveis via:
  - Regex (CPF, e-mail, IP, etc.)
  - NER com modelo `legal-bert-lgpd`
  - LLM local (via Ollama) — opcional
-  Modo seletivo ou agressivo de anonimização
-  Tema escuro ativável com toggle
-  Preview do texto anonimizado
- ⬇ Botão de download no formato escolhido
-  Logs salvos localmente com hash e timestamp
-  Containerizado com suporte a `docker-compose`

---

## Estrutura do Projeto


---

##  Executando a aplicação

### Modo local (sem Docker)

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .env
source .env/bin/activate  # Linux/mac
.env\Scripts\activate     # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute a aplicação
python run.py

# 3. Execute o ollama

ollama run mistral
