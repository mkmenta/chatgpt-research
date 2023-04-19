FROM ubuntu:focal
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9 
RUN apt install -y python3.9-dev
RUN apt install -y python3.9-distutils
RUN apt install -y wget
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.9 get-pip.py && rm get-pip.py
COPY requirements.txt /app/requirements.txt
RUN python3.9 -m pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
WORKDIR /app
# CMD [ "python3.9", "-m", "gunicorn", "--bind", "0.0.0.0:54928" "app:app"]