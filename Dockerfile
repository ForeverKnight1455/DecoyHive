
# Dockerfile for Kali GNU/Linux 2024.4
FROM kali:GNU/Linux

# Update and install basic tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*
