#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#                                                                                
#
# Import required Python libraries

# Fixing utf-8 issues when sending Snips intents in French with accents
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')

from thermostat import Thermostat
from hermes_python.hermes import Hermes
from snipshelpers.config_parser import SnipsConfigParser



CONFIG_INI =  "../config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

THERMOSTAT       = 'ericvde31830:thermostat'

def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    print(intentName, sentence)

with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(CONFIG_INI)


    except :
        config = None

    zibase =  None
    hostname = None
    ip=None
    thermostat = None

    if config and config.get('secret', None) is not None:
        if config.get('secret').get('ip_zibase', None) is not None:
            ip = config.get('secret').get('ip_zibase')
            if ip == "":
                ip = None

        print("Address ip zibase:{}").format(ip)
        for x, y in config.items():
            print(x, y)

    if ip is not None:
	try:
	    thermostat = Thermostat(ip)
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
