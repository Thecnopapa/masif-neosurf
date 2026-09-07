FROM --platform=linux/amd64 pymesh/pymesh:py3.6-slim

RUN echo "This is the pymesh:py3.6 image upgraded to debian bookworm (12)"
RUN echo "$(ls /etc/apt/sources)"


RUN sed -i 's/buster/bookworm/g' /etc/apt/sources.list

COPY ./sources.list /etc/apt/sources.list



RUN apt-get update -y --allow-insecure-repositories
RUN apt-get install debian-keyring debian-archive-keyring -y --allow-unauthenticated


RUN apt-get upgrade -y --allow-unauthenticated


CMD echo "$(cat /etc/apt/sources.list)" && echo "$(ls /etc/apt/sources.list.d)"