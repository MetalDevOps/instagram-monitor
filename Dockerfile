# Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY monitor.py .

# Create directories for data and logs
RUN mkdir data logs

CMD ["python", "monitor.py"]
