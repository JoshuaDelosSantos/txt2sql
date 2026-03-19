FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Add .dockerignore later!!

ENTRYPOINT [ "uvicorn" ]

CMD ["api:app", "--host", "0.0.0.0", "--port", "8000"]
