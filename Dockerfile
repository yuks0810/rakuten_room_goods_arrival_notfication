FROM python:3.6

ENV root_path /root/
WORKDIR ${root_path}
ADD . $root_path

RUN apt-get update && apt-get install -y unzip
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable zip

#install ChromeDriver
ADD https://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip /opt/chrome/

COPY Pipfile Pipfile.lock ./

# pipインストール(最新版)
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

RUN pip install pipenv \
    && pipenv install --dev
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN pipenv lock -r > requirements.txt && \
    pip install -r requirements.txt



RUN cd /opt/chrome/ && \
    unzip chromedriver_linux64.zip
ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome
ENTRYPOINT  ["/bin/sh", "-c", "while :; do sleep 10; done"]
