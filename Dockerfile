FROM ubuntu:16.04

RUN apt update && apt install -y \
        gcc \
        g++ \
        make \
        zip \
        jq \
        libgl-dev \
        libglu-dev \
        wget \
        nasm \
        xz-utils \
        python3 \
        git

ARG UNAME=myuser
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID $UNAME
USER $UNAME
WORKDIR /workdir
