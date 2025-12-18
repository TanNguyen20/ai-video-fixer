FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    yasm \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone https://github.com/anthwlock/untrunc.git . && \
    make && \
    cp untrunc /usr/local/bin/

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
