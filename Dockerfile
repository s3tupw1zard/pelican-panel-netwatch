FROM python:3.11-slim

WORKDIR /app

# Install Supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends supervisor && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the script and Supervisor configuration
COPY network_watcher.py /network_watcher.py
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Install Docker Python SDK
RUN pip install docker

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
