FROM buildpack-deps:jammy-curl

ARG TARGETARCH

# common tools
RUN apt update && export DEBIAN_FRONTEND=noninteractive \
    && apt -y install --no-install-recommends apt-utils vim htop expect-dev tini psmisc libgit2-dev

# build tools
RUN apt update && export DEBIAN_FRONTEND=noninteractive \
    && apt -y install --no-install-recommends openjdk-11-jdk protobuf-compiler libprotobuf-dev

CMD ["tail", "-f", "/dev/null"]