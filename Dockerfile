FROM python:3.10.17

# 將專案複製到容器中
COPY . /app
WORKDIR /app

# 安裝系統依賴（LibreOffice for .doc and .ppt conversion）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    libreoffice-impress \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8080
CMD uvicorn main:app --host=0.0.0.0 --port=$PORT