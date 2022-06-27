#!/bin/bash

echo ---Stopping and disabling services and daemons---

systemctl stop arancino-transmitter

systemctl disable arancino-transmitter

echo -------------------------------------------------
