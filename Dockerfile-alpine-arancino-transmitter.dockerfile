FROM alpine:3.18.6

RUN : \
    && apk update \
    && apk add vim wget nano curl python3 python3-dev linux-pam \
       gcc musl-dev linux-headers procps coreutils bash shadow \
       sudo net-tools libffi libffi-dev openssl openssl-dev sed \
       libusb libusb-dev libftdi1 libftdi1-dev avrdude openocd \
       g++ make libressl-dev libc-dev musl-dev build-base \
       bsd-compat-headers bash-completion cmake bluez\
    && :

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

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -v --no-cache-dir -r requirements.txt

# Copy the contents of tmp from the build context to the Docker image
COPY tmp/ .


# Estraggo il nome del file da pgk_name.txt
RUN ARANCINO_PACKAGE_FILE=$(cat pgk_name.txt) \
    && echo "Using Arancino package file: $ARANCINO_PACKAGE_FILE" \
    && pip3 install -v --no-cache-dir "$ARANCINO_PACKAGE_FILE"


COPY ./config/transmitter.cfg.yml /etc/arancino/config/transmitter.cfg.yml
