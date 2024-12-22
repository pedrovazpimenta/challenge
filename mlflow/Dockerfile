FROM python:3.11.9-slim-bullseye
# Install python packages
COPY requirements.txt .
RUN python3.11 -m pip install --upgrade pip setuptools wheel
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/* && rm -fr /root/.cache