FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies before copying the full source tree.
COPY app/requirements.txt ./app/requirements.txt

RUN pip install --no-cache-dir -r app/requirements.txt

COPY . .
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
