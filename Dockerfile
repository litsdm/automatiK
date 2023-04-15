FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

RUN apt update && apt-get -y install git wget \
    python3.10 python3.10-venv python3-pip \
    build-essential libgl-dev libglib2.0-0 vim
RUN ln -s /usr/bin/python3.10 /usr/bin/python

RUN useradd -ms /bin/bash banana
WORKDIR /app

RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
WORKDIR /app/stable-diffusion-webui

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD download_checkpoint.py .
RUN python download_checkpoint.py

ADD prepare.py .
RUN python prepare.py --skip-torch-cuda-test --xformers --reinstall-torch --reinstall-xformers

ADD download.py download.py
RUN python download.py --use-cpu=all

RUN mkdir -p extensions/banana/scripts
ADD script.py extensions/banana/scripts/banana.py
ADD app.py app.py

CMD ["python", "app.py", "--xformers", "--disable-safe-unpickle", "--lowram", "--no-hashing", "--listen"]

# FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

# WORKDIR /

# # Install git
# RUN apt-get update && apt-get install -y git

# # Install python packages
# RUN pip3 install --upgrade pip
# ADD requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt

# # Add your model weight files 
# # (in this case we have a python script)
# ADD download.py .
# RUN python3 download.py

# ADD . .

# EXPOSE 8000

# CMD python3 -u app.py