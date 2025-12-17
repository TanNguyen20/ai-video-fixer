# --- Stage 1: Build Untrunc ---
FROM ubuntu:22.04 AS builder
# Install build dependencies including ffmpeg development libraries
RUN apt-get update && apt-get install -y \
    git build-essential libavformat-dev libavcodec-dev libavutil-dev
RUN git clone https://github.com/anthwlock/untrunc.git /build
WORKDIR /build
RUN make

# --- Stage 2: API Runner ---
FROM python:3.10-slim

# Install the runtime shared libraries for ffmpeg
# Using the generic names ensures compatibility with the current Debian version
RUN apt-get update && apt-get install -y \
    libavformat-dev libavcodec-dev libavutil-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the compiled binary from the builder stage
COPY --from=builder /build/untrunc /usr/local/bin/untrunc
RUN chmod +x /usr/local/bin/untrunc

# Install API dependencies
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Create app directory
WORKDIR /app
COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
