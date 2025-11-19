# Dockerfile for the Rover WebRTC Python server
FROM python:3.11-slim

# Install system deps for OpenCV and ffmpeg/av
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libswscale-dev \
    libv4l-dev \
    v4l-utils \
    ffmpeg \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt /app/requirements.txt

# Install python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy server code
COPY . /app

# Create logs directory
RUN mkdir -p /app/logs && chown -R root:root /app/logs

ENV HOST=0.0.0.0
ENV PORT=3001

EXPOSE 3001

CMD ["python", "-u", "rover_webrtc.py"]
