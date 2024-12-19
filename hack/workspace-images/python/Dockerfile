FROM python:3.10-slim
RUN apt-get update && apt-get install -y curl sudo

#   Install the Python Language Server
RUN python3 -m pip install python-language-server

#   Install the Daytona CLI
RUN useradd -m daytona && echo "daytona ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/91-daytona
USER daytona

ARG DAYTONA_VERSION

RUN curl -sfL https://download.daytona.io/daytona/install.sh | DAYTONA_VERSION=${DAYTONA_VERSION} sudo -E bash

ENTRYPOINT [ "sleep", "infinity" ]