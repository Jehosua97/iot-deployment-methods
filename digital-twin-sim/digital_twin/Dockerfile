FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir paho-mqtt==2.1.0

COPY twin.py .

CMD ["python", "twin.py"]
