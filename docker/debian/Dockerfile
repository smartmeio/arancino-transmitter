FROM python:3.11-slim-bookworm

# defining user 'me'
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

ENV TZ 'Europe/Rome'

RUN mkdir -p $ARANCINO_HOME \
  && chown ${uid}:${gid} $ARANCINO_HOME \
  && groupadd -g ${gid} ${group} \
  && useradd -d "$ARANCINO_HOME" -u ${uid} -g ${gid} -m -s /bin/bash ${user} \
  && echo me:arancino | chpasswd \
  && echo root:arancino | chpasswd

# getting 'me' sudoer permissions
RUN echo "me ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

COPY ./extras/pip.conf /etc/pip.conf

WORKDIR $ARANCINO_HOME

COPY . $ARANCINO_HOME
RUN pip3 install --no-cache -r ./requirements.txt
RUN pip3 install -v --no-cache .

COPY ./config/transmitter.cfg.yml /etc/arancino/config/transmitter.cfg.yml

ENTRYPOINT [ "arancino-transmitter" ]
