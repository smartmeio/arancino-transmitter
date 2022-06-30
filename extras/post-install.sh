#!/bin/bash

source extras/vars-transmitter.env


echo ---------Making Logs and Conf directories--------
# create logs dir
echo creating directory: $ARANCINO
mkdir -p $ARANCINO

# create arancino dir
echo creating directory: $ARANCINOCONF
mkdir -p $ARANCINOCONF

echo creating directory: $ARANCINO/templates
mkdir -p $ARANCINO/templates

# create logs dir
echo creating directory: $ARANCINOLOG
mkdir -p $ARANCINOLOG

echo -------------------------------------------------

echo ---Giving grants 644 and copying services file---
chown 644 extras/arancino-transmitter.service
chown 644 config/transmitter.cfg.yml

cp extras/arancino-transmitter.service /etc/systemd/system/
cp extras/vars-transmitter.env /etc/arancino/
echo -------------------------------------------------


echo ------Backup previous configurations files-------
echo Backup previous configurations files
timestamp=$(date +%Y%m%d_%H%M%S)
[ -f /etc/arancino/config/transmitter.cfg.yml ] && mv $ARANCINOCONF/transmitter.cfg.yml $ARANCINOCONF/transmitter_$timestamp.cfg.yml
echo -------------------------------------------------

echo -------------------Copy files--------------------
cp config/transmitter.cfg.yml $ARANCINOCONF/transmitter.cfg.yml
cp config/transmitter.flow.smartme.cfg.yml $ARANCINOCONF/transmitter.flow.smartme.cfg.yml
cp config/transmitter.flow.stats.cfg.yml $ARANCINOCONF/transmitter.flow.stats.cfg.yml

cp templates/default.json.tmpl $ARANCINO/templates/default.json.tmpl
cp templates/default.xml.tmpl $ARANCINO/templates/default.xml.tmpl
cp templates/default.yaml.tmpl $ARANCINO/templates/default.yaml.tmpl
cp templates/S4T_default.json.tmpl $ARANCINO/templates/S4T_default.json.tmpl
cp templates/STATS_default.json.tmpl $ARANCINO/templates/STATS_default.json.tmpl
echo -------------------------------------------------

echo -------------Reloading daemons--------------------
systemctl daemon-reload

systemctl enable arancino-transmitter
systemctl restart arancino-transmitter
echo -------------------------------------------------
