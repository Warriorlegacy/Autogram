FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# FFmpeg with libass for zoompan + kinetic subtitle burn
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends ffmpeg libass-dev fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p workspace output

CMD ["python", "scripts/pipeline_reels.py"]
