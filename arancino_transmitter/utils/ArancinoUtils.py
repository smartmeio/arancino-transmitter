# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2020 SmartMe.IO

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


import logging
import sys
import os
import semantic_version
import arancino_transmitter
from datetime import datetime
from logging.handlers import RotatingFileHandler
from arancino_transmitter.ArancinoConstants import EnvType
import re
from typing import Any
import yaml
from yaml.parser import ParserError



#region ENV VARS NAME
EDGE_UUID = "EDGEUUID"

EDGE_MQTT_DATA_PWD = "EDGEMQTTDATAPWD"
EDGE_MQTT_DATA_USER = "EDGEMQTTDATAUSER"
EDGE_MQTT_DATA_PORT = "EDGEMQTTDATAPORT"
EDGE_MQTT_DATA_HOST = "EDGEMQTTDATAHOST"

FM_PROJ_NAME = "FMPROJNAME"     # Nome Progetto nel Fleet Manager
FM_FLEET_NAME = "FMFLEETNAME"   # Nome della Flotta nel Fleet Manager
FM_EDGE_NAME = "FMEDGENAME"     # Nome dell'Edge device nel Fleet Manager

A_ENV = "ARANCINOENV"           # Tipo di ambiente in cui sta girando il servizio
A_HOME = "ARANCINO"             # Wokring Directory di Arancino
A_CFG = "ARANCINOCONF"          # Directory dove si trovano i cfg file
A_LOG = "ARANCINOLOG"           # Directory dove si trovano i log file

#endregion

class Singleton:

    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class ArancinoEnvironment:


    def __init__(self):


        self._env = os.environ.get('ARANCINOENV')
        self._home_dir = os.environ.get('ARANCINO')
        self._cfg_dir = os.environ.get('ARANCINOCONF')
        self._log_dir = os.environ.get('ARANCINOLOG')
        self._tmplt_dir = os.path.join(self._home_dir, "templates")

        self._version = semantic_version.Version(arancino_transmitter.__version__)

        # Recupero il serial number / uuid dalla variabile di ambiente (quando sarà disponibile) altrimenti lo recupero dal seriale
        #   del dispositivo come veniva fatto in precedenza
        self._serial_number = os.getenv(EDGE_UUID) if os.getenv(EDGE_UUID) else self._retrieve_serial_number()

        self._fleet_manager_project_name = os.getenv(FM_PROJ_NAME)
        self._fleet_manager_fleet_name = os.getenv(FM_FLEET_NAME)
        self._fleet_manager_edge_name = os.getenv(FM_EDGE_NAME)

        self._sender_mqtt_host = os.getenv(EDGE_MQTT_DATA_HOST)
        self._sender_mqtt_user = os.getenv(EDGE_MQTT_DATA_USER)
        self._sender_mqtt_pwd = os.getenv(EDGE_MQTT_DATA_PWD)
        self._sender_mqtt_port = os.getenv(EDGE_MQTT_DATA_PORT)


    @property
    def sender_mqtt_host(self):
        return self._sender_mqtt_host


    @property
    def sender_mqtt_user(self):
        return self._sender_mqtt_user


    @property
    def sender_mqtt_pwd(self):
        return self._sender_mqtt_pwd


    @property
    def sender_mqtt_port(self):
        return self._sender_mqtt_port


    @property
    def env(self):
        return self._env


    @property
    def cfg_dir(self):
        return self._cfg_dir


    @property
    def version(self):
        return self._version


    @property
    def home_dir(self):
        return self._home_dir


    @property
    def log_dir(self):
        return self._log_dir


    @property
    def tmplt_dir(self):
        return self._tmplt_dir


    @property
    def serial_number(self):
        return self._serial_number
        #return self.__retrieve_serial_number()


    @property
    def fleet_manager_project_name(self):
        return self._fleet_manager_project_name


    @property
    def fleet_manager_fleet_name(self):
        return self._fleet_manager_fleet_name


    @property
    def fleet_manager_edge_name(self):
        return self._fleet_manager_edge_name


    # TODO: rivedere questo metodo.
    def _retrieve_serial_number(self):
        # Extract serial from cpuinfo file

        serial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    serial = line[10:26]
            f.close()
        except Exception as ex:
            try:
                f = open('cat /sys/class/dmi/id/product_uuid')
                serial = f.readline().strip()
                f.close()
            except Exception as ex:
                serial = "ERROR000000000"

        return serial

        #return self.__getMachine_addr()

    """
    def __getMachine_addr(self):

        try:

            os_type = sys.platform.lower()

            if "win" in os_type:
                command = "wmic bios get serialnumber"

            elif "linux" in os_type:
                command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"

            elif "darwin" in os_type:
                command = "ioreg -l | grep IOPlatformSerialNumber"

            return os.popen(command).read().replace("\n", "").replace("	", "").replace(" ", "")

        except Exception as ex:
            return "ERROR000000000"
    """


# @Singleton
# class ArancinoTransmitterConfig:

#     def __init__(self):
#         self.__yaml = YAML()#YAML(typ='safe', pure=True)

#         _env = ArancinoEnvironment.Instance().env
#         _cfg_dir = ArancinoEnvironment.Instance().cfg_dir
#         _cfg_file = ""
#         self.__files = []
#         self._cfgs = {}

#         from pathlib import Path
#         for yml_path in Path(_cfg_dir).glob("transmitter.flow.*.cfg.yml"):
#             self.__files.append(yml_path)

#         self.__open()



#     def __open(self):

#         for f in self.__files:
#             with open(f, "r") as ymlfile:
#                 #self._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
#                 y = self.__yaml.load(ymlfile)
#                 self._cfgs[y.get("flow").get("name").lower()] = y
#                 ymlfile.close()


#     def save(self, flow_name):
#         yaml = YAML()
#         file = os.path.join(ArancinoEnvironment.Instance().cfg_dir, "transmitter.flow.{}.cfg.yml".format(flow_name))
#         for f in self.__files:

#             if str(f) == file:
#                 with open(f, "w") as ymlfile:
#                     yaml.dump(self._cfgs[flow_name], ymlfile)
#                     ymlfile.close()
#                 break

#     @property
#     def cfgs(self):
#         return self._cfgs


@Singleton
class ArancinoConfig:

    _var_matcher = re.compile(r"\${([^}^{]+)}")
    _tag_matcher = re.compile(r"[^$]*\${([^}^{]+)}.*")

    def __init__(self):
        _env = ArancinoEnvironment.Instance().env
        _cfg_dir = ArancinoEnvironment.Instance().cfg_dir
        _cfg_file = ""


        if _env.upper() == EnvType.DEV \
                or _env.upper() == EnvType.TEST \
                or _env.upper() == EnvType.DEVELOPMENT:
            _cfg_file = "transmitter.dev.cfg.yml"

        elif _env.upper() == EnvType.PROD \
                or _env.upper() == EnvType.PRODUCTION:
            _cfg_file = "transmitter.cfg.yml"


        self.__file = os.path.join(_cfg_dir, _cfg_file)

        self.__open()

    def _path_constructor(self, _loader: Any, node: Any):

        def parse_default_value(s):
            try:
                return int(s) if s.isdigit() else float(s) if "." in s else complex(s)
            except (ValueError, AttributeError):
                return s

        def replace_fn(match):
            envparts = f"{match.group(1)}:".split(":")
            return os.environ.get(envparts[0], envparts[1])
        return parse_default_value(self._var_matcher.sub(replace_fn, node.value))


    def __open(self):
        yaml.add_implicit_resolver("!envvar", self._tag_matcher, None, yaml.SafeLoader)
        yaml.add_constructor("!envvar", self._path_constructor, yaml.SafeLoader)
        try:
            with open(self.__file, "r") as f:
                self._cfg = yaml.safe_load(f.read())
                return  self._cfg
        except (FileNotFoundError, PermissionError, ParserError):
            return  self._cfg

    def save(self):
        with open(self.__file, 'w') as yaml_file:
            yaml.dump(self._cfg, yaml_file, default_flow_style=False)
            yaml_file.close()
        self.__open()


    @property
    def cfg(self):
        return self._cfg


@Singleton
class ArancinoLogger:

    def __init__(self):
        self.__logger = None

        # logger configuration
        CONF = ArancinoConfig.Instance().cfg
        ENV = ArancinoEnvironment.Instance()

        self.__name = CONF.get("log").get("name")
        self.__filename = CONF.get("log").get("file_log") # 'arancino.log'
        self.__error_filename = CONF.get("log").get("file_error")   # 'arancino.error.log'

        # __dirlog = Config["log"].get("path")           #'/var/log/arancino'
        self.__dirlog = ENV.log_dir     #os.environ.get('ARANCINOLOG')
        self.__format = CustomConsoleFormatter(level='DEBUG')  #logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.__log_size = CONF.get("log").get("size")
        self.__log_rotate = CONF.get("log").get("rotate")

        # logging.basicConfig(level=logging.getLevelName(CONF.get_log_level()))
        # if CONF.get_log_handler_console():
        #     logging.handlers


        self.__logger = logging.getLogger(self.__name) #CustomLogger(self.__name)#
        self.__logger.setLevel(logging.getLevelName(CONF.get("log").get("level")))

        if CONF.get("log").get("handler_console"):
            self.__logger.addHandler(self.__getConsoleHandler())

        if CONF.get("log").get("handler_file"):
            self.__logger.addHandler(self.__getFileHandler())
            self.__logger.addHandler(self.__getErrorFileHandler())

    def __getConsoleHandler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.__format)
        return console_handler

    def __getFileHandler(self):
        file_handler = RotatingFileHandler(os.path.join(self.__dirlog, self.__filename), encoding='utf-8', mode='a', maxBytes=1000 * 1024 * self.__log_size, backupCount=self.__log_rotate)
        file_handler.setFormatter(self.__format)
        return file_handler

    def __getErrorFileHandler(self):
        file_handler_error = RotatingFileHandler(os.path.join(self.__dirlog, self.__error_filename), mode='a', maxBytes=1000 * 1024 * self.__log_size, backupCount=self.__log_rotate)
        file_handler_error.setFormatter(self.__format)
        file_handler_error.setLevel(logging.ERROR)
        return file_handler_error

    def getLogger(self):
        return self.__logger
        # return logging


class CustomConsoleFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    """Based on https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level"""


    def __init__(self, level="INFO"):
        self.__level = level

        format_pre = "%(asctime)s - %(name)s : %(filename)s: - "
        format_post = "%(levelname)s - %(message)s"

        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        blue = '\x1b[94:21m'
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        #format_pre = "%(asctime)s - %(name)s - "
        if self.__level.upper() == 'DEBUG':
            format_pre = "%(asctime)s - %(name)s : %(threadName)s.%(filename)s.%(funcName)s:%(lineno)d - "


        self.FORMATS = {
            logging.DEBUG: format_pre + grey + format_post + reset,
            logging.INFO: format_pre + blue + format_post + reset,
            logging.WARNING: format_pre + yellow + format_post + reset,
            logging.ERROR: format_pre + red + format_post + reset,
            logging.CRITICAL: format_pre + bold_red + format_post + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def stringToBool(value):
    '''
    Convert a string representation of boolean value to an object of type Bool.
    :param value: {String) Value to convert
    :return: {Bool} Boolean conversion
    '''
    if value is not None:
        __val = (value.upper() == "TRUE")
    else:
        __val = False

    return __val


def stringToBool2(value):
    list_true = ["true", "1", "yes", "y", "t"]
    list_false = ["false", "0", "no", "n", "f"]

    __val = False
    if value is not None:
        v = str(value).lower()

        if v in list_true:
            __val = True
        elif v in list_false:
            __val = False
        
    return __val


def stringToDatetime(dt_str):
    dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
    return dt


def datetimeToString(dt):
    dt_str = dt.strftime("%Y.%m.%d %H:%M:%S")
    return dt_str


def secondsToHumanString(total_seconds):
    # https://thesmithfam.org/blog/2005/11/19/python-uptime-script/

    # Helper vars:
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24

    # Get the days, hours, etc:
    days = int(total_seconds / DAY)
    hours = int((total_seconds % DAY) / HOUR)
    minutes = int((total_seconds % HOUR) / MINUTE)
    seconds = int(total_seconds % MINUTE)

    # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    string = ""
    if days > 0:
        string += str(days) + " " + (days == 1 and "day" or "days") + ", "
    if len(string) > 0 or hours > 0:
        string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
    if len(string) > 0 or minutes > 0:
        string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "
    string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")

    return string
