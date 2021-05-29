FROM python:3.6
USER root

ENV APP_ROOT /webapp
WORKDIR $APP_ROOT

COPY . $APP_ROOT

RUN apt-get update && apt-get install -y unzip
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable zip python-pip

# pipインストール(最新版)
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py

RUN pip install pipenv
# RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt
RUN pip install webdriver-manager

ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome
ENTRYPOINT  ["/bin/sh", "-c", "while :; do sleep 10; done"]
