FROM python:3.9-slim

WORKDIR /app

RUN mkdir -p /app/data /app/output /app/logs
RUN chmod 777 /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "echo 'Starting Flask app...' && python app.py"]