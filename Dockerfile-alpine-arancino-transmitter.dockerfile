FROM alpine:3.18.6

RUN : \
    && apk update \
    && apk add python3 python3-dev bash


ARG user=me
ARG group=me
ARG uid=1000
ARG gid=1000
ARG http_port=8080
ARG agent_port=50000
ARG ARANCINO_HOME=/home/me

ENV ARANCINO_HOME $ARANCINO_HOME

# Arancino is run with user `me`, uid = 1000
# If you bind mount a volume from the host or a data container,
# ensure you use the same uid
RUN mkdir -p $ARANCINO_HOME \
  && chown ${uid}:${gid} $ARANCINO_HOME \
  && addgroup -g ${gid} ${group} \
  && adduser -h "$ARANCINO_HOME" -u ${uid} -G ${group} -s /bin/bash -D ${user} \
  && echo me:arancino | chpasswd \
  && echo root:arancino | chpasswd

RUN wget -qO- https://bootstrap.pypa.io/pip/get-pip.py | python3

COPY ./extras/pip.conf /etc/pip.conf

# Create a temporary directory in the Docker image
WORKDIR /tmp

# Copy the contents of tmp from the build context to the Docker image
COPY tmp/ .



# Estraggo il nome del file da pgk_name.txt
RUN ARANCINO_PACKAGE_FILE=$(cat pgk_name.txt) \
    && echo "Using Arancino package file: $ARANCINO_PACKAGE_FILE" \
    && pip3 install -v --no-cache-dir "$ARANCINO_PACKAGE_FILE"


COPY ./config/transmitter.cfg.yml /etc/arancino/config/transmitter.cfg.yml
