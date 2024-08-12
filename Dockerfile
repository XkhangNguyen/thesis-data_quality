FROM python:3.10-slim-bullseye

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app/ .
RUN pip install --no-cache-dir -r requirements.txt 

ENTRYPOINT [ "python", "main.py" ]

