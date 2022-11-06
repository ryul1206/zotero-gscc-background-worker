FROM python:3.8.15-alpine

WORKDIR /root

COPY worker/*.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && touch secret_cfg.yml

CMD ["python", "main.py", "secret_cfg.yml"]