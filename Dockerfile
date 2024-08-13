FROM python:3.10-slim-bullseye
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app/ .

ENTRYPOINT [ "python3", "main.py" ]

