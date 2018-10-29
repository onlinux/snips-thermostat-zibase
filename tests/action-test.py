#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#
#   __     _                             _                    _            _      
#  /__\ __(_) ___  /\   /\__ _ _ __   __| | ___  ___ __ _ ___| |_ ___  ___| | ___ 
# /_\| '__| |/ __| \ \ / / _` | '_ \ / _` |/ _ \/ __/ _` / __| __/ _ \/ _ \ |/ _ \
#//__| |  | | (__   \ V / (_| | | | | (_| |  __/ (_| (_| \__ \ ||  __/  __/ |  __/
#\__/|_|  |_|\___|   \_/ \__,_|_| |_|\__,_|\___|\___\__,_|___/\__\___|\___|_|\___|
#                                                                                 
#
# Import required Python libraries
import settings
from thermostat import Thermostat
import time
from hermes_python.hermes import Hermes
import requests
from snipshelpers.config_parser import SnipsConfigParser

# Fixing utf-8 issues when sending Snips intents in French with accents
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

CONFIG_INI =  "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

THERMOSTAT       = 'ericvde31830:thermostat'

def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    print(intentName)

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
            
    if ip is not None:
	try:
	    thermostat = Thermostat(ip)
	    thermostat.setSetpointDay(203)
	    thermostat.setSetpointNight(195)
	    thermostat.addSetpointDay(1)
	    thermostat.addSetpointNight(5)
	    thermostat.setMode(16)
	    thermostat.update()
	    
	    thermostat.read()
	    
	except Exception as e:
            zibase = None
            print('Error Thermostat {}'.format(e))
        
    h.subscribe_intents(intent_received).start()
