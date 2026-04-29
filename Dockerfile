FROM python:3.10-slim

# Instala dependências do sistema (essencial para o OCR funcionar)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o requirements.txt primeiro para aproveitar o cache de camadas
COPY requirements.txt .

# Instala as bibliotecas Python (aqui ele vai ler o pypdf novo)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código (app.py)
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]