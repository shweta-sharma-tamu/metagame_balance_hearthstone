# base image
FROM ubuntu:18.04

# updates, upgrades, common instalation
RUN apt-get -y update &&\
    apt-get -y upgrade &&\
    apt-get -y install software-properties-common

# python3 install
RUN add-apt-repository -y ppa:deadsnakes/ppa &&\
    apt-get -y update &&\
    apt-get -y install python3.8 &&\
    apt-get -y install python3.8-venv &&\
    apt-get -y install python3.8-dev &&\
    apt-get -y install python3-pip


# pip upgrade
RUN python3.8 -m pip install --user --upgrade pip

# install and create virtualenv
RUN python3.8 -m pip install --user virtualenv &&\
    python3.8 -m venv vgc-env

# git install
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install git

# vgc ai framework repository clone
RUN git clone https://gitlab.com/DracoStriker/pokemon-vgc-engine.git vgc-ai

RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

RUN apt-get -y install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev &&\
    apt-get -y install libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk &&\
    apt-get -y install libharfbuzz-dev libfribidi-dev libxcb1-dev &&\
    apt-get -y install build-essential libssl-dev libffi-dev python-dev &&\
    apt-get -y update &&\
    apt-get -y install patchelf


# install requirements
RUN . vgc-env/bin/activate &&\
python3.8 -m pip install cython==0.29.30 &&\
python3.8 -m pip install wheel &&\
    python3.8 -m pip install -r vgc-ai/requirements.txt

# SSH
EXPOSE 22
RUN apt-get -y install openssh-server &&\
    mkdir -p /var/run/sshd

# authorize SSH connection with root account
RUN sed -i 's/PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config

# change password root
RUN echo "root:vgc"|chpasswd

# Run SSH
CMD service ssh start -D

# Add vgc framework to python path
ENV PYTHONPATH "${PYTHONPATH}:/vgc-ai/"
