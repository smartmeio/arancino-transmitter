FROM python:3.11-slim-bookworm

# defining user 'me'
ARG user=me
ARG group=me
ARG uid=1000
ARG gid=1000
ARG ARANCINO_HOME=/home/me

ENV TZ 'Europe/Rome'

RUN mkdir -p $ARANCINO_HOME \
  && chown ${uid}:${gid} $ARANCINO_HOME \
  && groupadd -g ${gid} ${group} \
  && useradd -d "$ARANCINO_HOME" -u ${uid} -g ${gid} -m -s /bin/bash ${user} \
  && echo me:arancino | chpasswd \
  && echo root:arancino | chpasswd

# getting 'me' sudoer permissions
RUN echo "me ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Aggiornamento e installazione dei pacchetti di sistema
# Aggiornamento e installazione dei pacchetti di sistema
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      gnupg apt-transport-https git nano \
      gcc musl-dev python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installazione di ruamel.yaml.clib
RUN pip3 install ruamel.yaml.clib
COPY ./extras/pip.conf /etc/pip.conf

# Create a temporary directory in the Docker image
WORKDIR /tmp

# Copy the contents of tmp from the build context to the Docker image
COPY tmp/ .



# Estraggo il nome del file da pgk_name.txt
RUN ARANCINO_DEBIAN_PACKAGE_FILE=$(cat pgk_name.txt) \
    && echo "Using Arancino package file: $ARANCINO_DEBIAN_PACKAGE_FILE" \
    && pip3 install -v --no-cache-dir "$ARANCINO_DEBIAN_PACKAGE_FILE"


COPY ./config/transmitter.cfg.yml /etc/arancino/config/transmitter.cfg.yml

#CMD [ "arancino-transmitter" ]
