FROM python:3.12-slim

WORKDIR /app

COPY server.py .
COPY fixtures.json .

EXPOSE 8080

CMD ["python", "server.py"]
