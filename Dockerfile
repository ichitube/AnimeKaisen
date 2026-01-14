FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl tini ca-certificates build-essential \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["python","main.py"]
