#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#
#
#
# Import required Python libraries

from thermostat import Thermostat
from hermes_python.hermes import Hermes
from snipshelpers.config_parser import SnipsConfigParser

# Fixing utf-8 issues when sending Snips intents in French with accents
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

CONFIG_INI = "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

THERMOSTAT = 'ericvde31830:thermostat'


def open_thermostat(config):
    ip = config.get(
        'secret', {
            "ip": "192.168.0.100"}).get(
        'ip', '192.168.0.100')
    tempVariableId = int(
        config.get(
            'global', {
                "tempVariable": "28"}).get(
            'tempVariable', '28'))
    setpointDayVariableId = config.get(
        'global', {
            "setpointDayVariable": "29"}).get(
        'setpointDayVariable', '29')
    setpointNightVariableId = config.get(
        'global', {
            "setpointNightVariable": "29"}).get(
        'setpointNightVariable', '30')
    modeVariableId = config.get(
        'global', {
            "modeVariable": "29"}).get(
        'modeVariable', '31')
    stateVariableId = config.get(
        'global', {
            "stateVariable": "13"}).get(
        'stateVariable', '13')
    thermostatScenarioId = config.get(
        'global', {
            "thermostatScenario": "32"}).get(
        'thermostatScenario', '32')

    thermostat = Thermostat(
        ip,
        int(tempVariableId),
        int(setpointDayVariableId),
        int(setpointNightVariableId),
        int(modeVariableId),
        int(stateVariableId),
        int(thermostatScenarioId))

    print(" Address ip zibase:{}").format(ip)
    print("Indoor Temperature:{}").format(
        thermostat.tempStr(thermostat.getTemp() / 10.0))

    return thermostat


def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    print(intentName, sentence)


with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(CONFIG_INI)

    except BaseException:
        config = None

    thermostat = None

    try:
        thermostat = open_thermostat(config)
        #thermostat = Thermostat(ip)
        thermostat.setSetpointDay(207)
        thermostat.setSetpointNight(195)
        thermostat.addSetpointDay(1)
        thermostat.addSetpointNight(5)
        thermostat.setMode(0)
        thermostat.update()
        thermostat.read()

    except Exception as e:
        zibase = None
        print('Error Thermostat {}'.format(e))

    h.subscribe_intents(intent_received).start()
