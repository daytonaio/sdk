FROM node:23-slim
RUN apt-get update && apt-get install -y curl sudo
#   Install the TypeScript Language Server
RUN npm i -g typescript-language-server
#   Install the Daytona CLI
RUN useradd -m daytona && echo "daytona ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/91-daytona
USER daytona

ARG DAYTONA_VERSION

RUN curl -sfL https://download.daytona.io/daytona/install.sh | DAYTONA_VERSION=${DAYTONA_VERSION} sudo -E bash

RUN sudo chmod -R 777 /home/daytona

ENTRYPOINT [ "sleep", "infinity" ]