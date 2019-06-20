FROM python:3.6-slim

WORKDIR /build

RUN apt-get -y update && apt-get -y install netcat

COPY requirements.txt /build

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /exec

COPY bootstrap.sh /exec

VOLUME '/static'

WORKDIR /code

COPY mastermind /code

CMD ["/exec/bootstrap.sh"]

EXPOSE 8000