from nginx:alpine
RUN apk add python3 tzdata

# Set the timezone
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./halo /opt/app
WORKDIR /opt/app
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

