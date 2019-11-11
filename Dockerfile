from nginx:alpine
RUN apk add python3
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./halo /opt/app
WORKDIR /opt/app
RUN chmod +x entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

