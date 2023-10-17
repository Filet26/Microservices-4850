FROM python:3.10-slim
LABEL maintainer="dho95@my.bcit.ca"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "python", "app.py" ]
