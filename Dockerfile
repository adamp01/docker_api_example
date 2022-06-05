FROM python:3.9.5-slim-buster

MAINTAINER Adam Wood "adam.wood@system1.com"

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat libpcre3 libpcre3-dev build-essential

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 5000

RUN useradd -r -u 1001 wsgi && \
    chown -R wsgi:wsgi /app && \
    chmod +x /app/entrypoint.sh

USER wsgi

ENTRYPOINT ["/app/entrypoint.sh"]
