FROM alpine:3.6

EXPOSE 8000

RUN apk add --no-cache \    
        build-base \
        linux-headers \
        musl-dev \
        postgresql-dev \
        uwsgi \
        uwsgi-python3 \
        python3 \
        python3-dev \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        jpeg-dev \
        openjpeg-dev

RUN pip3 install --upgrade pip 
RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade Incremental
ADD requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip3 install --no-cache-dir -r requirements.txt
ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
