FROM python:3.11.9-slim-bullseye

ADD . /app
WORKDIR /app

RUN python3.11 -m pip install --upgrade pip setuptools wheel
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/* && rm -fr /root/.cache

EXPOSE 8000
CMD uvicorn main:app --host=0.0.0.0 --port=8000 --log-config=log_conf.yaml