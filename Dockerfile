FROM python:3.6
USER root

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y zip
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv \
    && pipenv --python /usr/local/bin/python install --dev
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
ENTRYPOINT  ["/bin/sh", "-c", "while :; do sleep 10; done"]
