FROM alpine:3.18.6

RUN : \
    && apk update \
    && apk add --no-cache py3-pip bash

ARG user=me
ARG group=me
ARG uid=1000
ARG gid=1000
ARG ARANCINO_HOME=/home/me

ENV ARANCINO_HOME $ARANCINO_HOME
ENV ARANCINO=/etc/arancino
ENV ARANCINOCONF=/etc/arancino/config
ENV ARANCINOLOG=/var/log/arancino
ENV ARANCINOENV=PROD

# Arancino is run with user `me`, uid = 1000
# If you bind mount a volume from the host or a data container,
# ensure you use the same uid

RUN mkdir -p $ARANCINO_HOME \
  && chown ${uid}:${gid} $ARANCINO_HOME \
  && addgroup -g ${gid} ${group} \
  && adduser -h "$ARANCINO_HOME" -u ${uid} -G ${group} -s /bin/bash -D ${user} \
  && echo me:arancino | chpasswd \
  && echo root:arancino | chpasswd

COPY ./extras/pip.conf /etc/pip.conf

WORKDIR $ARANCINO_HOME
COPY . $ARANCINO_HOME
RUN pip3 install -v --no-cache .

COPY ./config/transmitter.cfg.yml /etc/arancino/config/transmitter.cfg.yml

ENTRYPOINT [ "arancino-transmitter" ]
