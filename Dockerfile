from nginx:alpine
RUN apk add python3
COPY ./halo /opt/app
WORKDIR /opt/app
RUN pip3 install -r requirements.txt

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

