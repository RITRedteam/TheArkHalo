from nginx:alpine
RUN apk add python3
COPY . /opt/app
WORKDIR /opt/app
RUN pip3 install requests

ENTRYPOINT ["entrypoint.sh"]

