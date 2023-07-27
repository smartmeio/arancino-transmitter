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

from arancino_transmitter.transmitter.parser.ParserSimple import ParserSimple
from arancino_transmitter.ArancinoDataStore import ArancinoDataStore
from arancino_transmitter.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")
ENV = ArancinoEnvironment.Instance()



class ParserS4T(ParserSimple):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)
        #private

        #self.__db_name = CONF.get_transmitter_parser_s4t_db_name()
        self.__db_name = self.cfg.get("s4t").get("db_name")

        self.__fm_proj_name = ENV.fleet_manager_project_name if ENV.fleet_manager_project_name else self.cfg.get("s4t").get("fleet_manager_project_name")
        self.__fm_fleet_name = ENV.fleet_manager_fleet_name if ENV.fleet_manager_fleet_name else self.cfg.get("s4t").get("fleet_manager_fleet_name")
        self.__fm_edge_name = ENV.fleet_manager_edge_name if ENV.fleet_manager_edge_name else self.cfg.get("s4t").get("fleet_manager_edge_name")

        # Redis Data Stores
        redis = ArancinoDataStore.Instance()
        self.__datastore_dev = redis.getDataStoreDev()

        #protected
    
    def _do_elaboration(self, data=None):

        rendered_data, metadata = super()._do_elaboration(data)

        if metadata:
            for index, md in enumerate(metadata):
                md["tags"] = data[index]["tags"]
                md["tags"]["fm_proj_name"] = self.__fm_proj_name
                md["tags"]["fm_fleet_name"] = self.__fm_fleet_name
                md["tags"]["fm_edge_name"] = self.__fm_edge_name

                md["labels"] = data[index]["labels"]

                port_id = data[index]["labels"]["port_id"]
                port_alias = self.__datastore_dev.hget(port_id, "C_ALIAS")
                if port_alias:
                    md["labels"]["port_alias"] = port_alias

                #md["db_name"] = self.__db_name
        
        return rendered_data, metadata


