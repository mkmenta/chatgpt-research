FROM ubuntu:focal
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9 
RUN apt install -y python3.9-dev
RUN apt install -y python3.9-distutils
RUN apt install -y wget
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.9 get-pip.py
COPY . /app
WORKDIR /app
RUN python3.9 -m pip install -r requirements.txt
ENV FLASK_APP=app
CMD python3.9 -m flask run --host=0.0.0.0
