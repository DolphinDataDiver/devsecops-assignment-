FROM python:3.12-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY api/ .

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]

