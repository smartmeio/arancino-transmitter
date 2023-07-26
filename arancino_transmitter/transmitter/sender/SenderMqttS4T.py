# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 smartme.IO

Authors:  Sergio Tomasello <sergio@smartme.io>

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License
"""

from arancino_transmitter.transmitter.sender.SenderMqtt import SenderMqtt
from arancino_transmitter.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")
ENV = ArancinoEnvironment.Instance()

class SenderMqttS4T(SenderMqtt):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)
        
    def _do_trasmission(self, data=None, metadata=None):
        '''

        Implementazione del metodo do_transmission della classe concreta SenderMqttS4T

        :param data: contiene le metriche
        :param metadata: contiene dati aggiuntivi per caratterizzare la metrica, solitamente
            contiene: key, flow_name, tags, labels
        :return:
        '''

        # tags sono una serie di dati passati nel topic che servono al nostro sistema cloud,
        # con lo scopo di caratterizzare la metrica
        tags = ""


        # estrae dai metadata le labels e le inserisce come tags
        # solitamente labels contiene le chiavi: device_id, port_id, port_type
        for key, value in metadata["labels"].items():
            tmp = "{}={}".format(key, value)
            tags += tmp + '/'

        # estrae dai metadata i tags e li inserisce come tags
        for key, value in metadata["tags"].items():
            tmp = "{}={}".format(key, value)
            tags += tmp + '/'


        # key rappresenta il nome della metrica ed è composta dalla
        # coppia "port_id:key". Quindi tramite split prendo il secondo
        # elemento alla posizione 1. Ciò che viene estratto a sua volta
        # potrebbe contenere informazioni sulla sorgente/canale della metrica
        # di conseguenza se presente il simbolo "-" viene eseguito ulteriore split
        # se non presente aggiungo come tag della metrica la coppia "channel=0"

        full_field = metadata["key"].split(':')[1]
        field = full_field
        channel = "0"

        if '#' in full_field:
            field, channel = full_field.split('#')

        tags += "channel={}/".format(channel)
        #self._topic = "{}/{}{}".format(metadata["db_name"], tags, field)
        self._topic = "{}/{}{}".format(self.cfg.get("mqtt").get("topic"), tags, field)

        return super()._do_trasmission(data=data, metadata=metadata)