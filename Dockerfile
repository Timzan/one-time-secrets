FROM python:3.7

ENV DOCKER_MACHINE_IP=192.168.99.100

WORKDIR /app

ADD . /app


RUN pip3 install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["main.py"]

