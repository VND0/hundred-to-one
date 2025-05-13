FROM ubuntu:24.04

WORKDIR /certbot
COPY . .

RUN apt-get update && apt-get upgrade
RUN apt-get install -y certbot

CMD ["bash", "generate-certificate.sh"]
