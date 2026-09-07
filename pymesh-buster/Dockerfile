FROM --platform=linux/amd64 pymesh/pymesh:py3.6-slim


RUN sed -i 's/http/[check-valid-until=no] http/g' /etc/apt/sources.list

RUN sed -i 's/deb.debian/archive.debian/g' /etc/apt/sources.list
RUN sed -i 's/security.debian/archive.debian/g' /etc/apt/sources.list

RUN apt-get update -y --allow-insecure-repositories
#RUN apt-get install debian-keyring debian-archive-keyring -y --allow-unauthenticated


RUN apt-get upgrade -y --allow-unauthenticated


CMD  echo "This is the updated pymesh:py3.6 (dedian buster)" && echo "$(cat /etc/apt/sources.list)" && echo "$(ls /etc/apt/sources.list.d)"