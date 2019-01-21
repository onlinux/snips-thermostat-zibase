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
from Zapi import ZiBase
import time




CONFIG_INI =  "../config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

THERMOSTAT       = 'ericvde31830:thermostat'
def ledBlink(led):
    if led > 5 or led < 0:
        led = 1

    zibase.setVariable(5, 2)
    time.sleep( 3 )
    zibase.runScenario(led + 58)

def ledOn(led):
    if led > 5 or led < 0:
        led = 1

    time.sleep( 5 )
    zibase.setVariable(5, 1)

    zibase.runScenario(led + 58)

def ledOff(led):
    if led > 5 or led < 0:
        led = 1

    zibase.setVariable(5, 0)
    time.sleep( 3 )
    zibase.runScenario(led + 58)

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
        zibase = ZiBase.ZiBase(ip)
        #ledBlink(1)
        ledOn(2)
        #ledBlink(5)
        time.sleep( 3 )
        for l in range(6):
            ledOff(l)


        # for v5 in range(3):
        #
        #
        #     zibase.setVariable(5, v5)
        #     zibase.runScenario(59)
        #     print zibase.getVariable(5)
        #
        #
        #
        #     zibase.runScenario(60)
        #     print zibase.getVariable(5)
        #
        #
        #
        #     zibase.runScenario(61)
        #     print zibase.getVariable(5)
        #
        #
        #
        #     zibase.runScenario(62)
        #     print zibase.getVariable(5)
        #
        #
        #
        #     zibase.runScenario(63)
        #     print zibase.getVariable(5)
        #
        #     time.sleep( 5 )


    #h.subscribe_intents(intent_received).start()
