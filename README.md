# Crie ambiente virtual
python -m venv .env
source .env/bin/activate  # Linux/macOS
.env\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

docker build -t anonim-lgpd .
docker run -p 5000:5000 anonim-lgpd

ollama run mistral

Os arquivos anonimizados ficam salvos em logs/.

