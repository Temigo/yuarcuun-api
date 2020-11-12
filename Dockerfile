#Download base image ubuntu 18.04
FROM ubuntu:18.04


LABEL maintainer="[email protected]"
LABEL version="0.1"
LABEL description="blah"

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update

RUN apt -y install dpkg-dev g++ gcc binutils git python-dev python-pip python-setuptools wget
RUN pip --no-cache-dir install

RUN apt install -y ffmpeg
RUN apt install -y python-libhfst
