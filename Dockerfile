FROM python:3.12

WORKDIR /usr/src/app
COPY . .

RUN apt update && apt install -y --no-install-recommends npm && npm i && pip install -r requirements.txt

EXPOSE 80
ENTRYPOINT ["python", "main.py"]