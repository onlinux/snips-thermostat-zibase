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
THERMOSTATSET = 'ericvde31830:ZibaseThermostatSet'
THERMOSTATSHIFT = 'ericvde31830:thermostatShift'
THERMOSTATTURNOFF = 'ericvde312830:thermostatTurnOff'


def open_thermostat(config):
    ip = config.get(
        'secret', {
            "ip": "192.168.0.100"}).get(
        'ip', '192.168.0.100')
    tempVariableId = int(
        config.get(
            'global', {
                "tempvariable": "28"}).get(
            'tempvariable', '28'))
    setpointDayVariableId = config.get(
        'global', {
            "setpointdayvariable": "29"}).get(
        'setpointdayvariable', '29')
    setpointNightVariableId = config.get(
        'global', {
            "setpointnightvariable": "29"}).get(
        'setpointnightvariable', '30')
    modeVariableId = config.get(
        'global', {
            "modevariable": "29"}).get(
        'modevariable', '31')
    stateVariableId = config.get(
        'global', {
            "statevariable": "13"}).get(
        'statevariable', '13')
    thermostatScenarioId = config.get(
        'global', {
            "thermostatscenario": "32"}).get(
        'thermostatscenario', '32')
    thermostatProbeId = config.get(
        'global', {
            "thermostatprobeid": "13"}).get(
        'thermostatprobeid', '13')

    thermostat = Thermostat(
        ip,
        int(tempVariableId),
        int(setpointDayVariableId),
        int(setpointNightVariableId),
        int(modeVariableId),
        int(stateVariableId),
        int(thermostatScenarioId),
        int(thermostatProbeId))

    print(" Address ip zibase:{}").format(ip)
    print(" Indoor Temperature:{}").format(
        thermostat.tempStr(thermostat.getTemp() / 10.0))
    print (" Thermostat Mode:{}").format(thermostat.getModeString())
    print (" Thermostat State:{}").format(thermostat.getStateString())
    print (" Thermostat running Mode:{}").format(
        thermostat.getRunningModeString())
    return thermostat


def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    print intentName

    for (slot_value, slot) in intent_message.slots.items():
        print('Slot {} -> \n\tRaw: {} \tValue: {}'
              .format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))


    if intentName == THERMOSTATTURNOFF:

        print "Thermostat turnOff"
        if intent_message.slots.temperature_device:
            thermostat.setMode(48)  # Turn nightMode on
            sentence = "Ok, je passe en mode nuit."
            print sentence
            hermes.publish_end_session(intent_message.session_id, sentence)
            return


    if intentName == THERMOSTATSET:
        if intent_message.slots.temperature_decimal:
            temperature = intent_message.slots.temperature_decimal.first().value
            print "Température reconnue:", temperature
            runningMode = thermostat.getRunningModeString()
            runMode = thermostat.getModeString()

            if runningMode == 'nuit':
                thermostat.setSetpointNight(int(temperature) )

            elif runningMode == 'jour':
                thermostat.setSetpointDay(int(temperature) )

            thermostat.update()
            sentence = "Ok, je passe la consigne de {} à {} degrés".format(
                runningMode, str(temperature/10.0))
            hermes.publish_end_session(intent_message.session_id, sentence)
            return

    if intentName == THERMOSTATSHIFT:
        if intent_message.slots.up_down:
            up_down = intent_message.slots.up_down.first().value
            action = up_down.encode('utf-8')
            print "intent_message.slots.up_down.first()", action

            if action is not None:

                setPoint = None
                runningMode = thermostat.getRunningModeString()
                runMode = thermostat.getModeString()
                print "runningMode: {}, runMode: {}".format(
                    runningMode, runMode
                )
                if runMode == 'stop' or runMode == 'hors gel':
                    sentence = "Désolée mais nous sommes en mode {}. Je ne fais rien dans ce cas.".format(
                        runMode)
                elif action == 'down':
                    if runningMode == 'jour' or "jour" in thermostat.getModeString():
                        thermostat.addSetpointDay(-1)
                        setPoint = str(thermostat.getSetpointDay()
                                       / 10.0).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je descends donc la consigne de jour à {} degrés.".format(
                            runMode, setPoint)
                    else:
                        thermostat.addSetpointNight(-1)
                        setPoint = str(thermostat.getSetpointNight()
                                       / 10.0).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je descends donc la consigne de nuit à {} degrés.".format(
                            runMode, setPoint)

                elif action == "up":
                    if "nuit" not in runMode and runningMode == 'jour' or "jour" in runMode :
                        thermostat.addSetpointDay(1)
                        setPoint = str(thermostat.getSetpointDay()
                                       / 10.0).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je monte la consigne de jour à {} degrés.".format(
                            runMode, setPoint)
                    else:
                        # switch to mode tempo-jour
                        if runningMode == 'nuit' and runMode == 'automatique':
                            sentence = "Nous sommes en mode {} économique, je passe donc en mode tempo jour".format(
                                runMode)
                        else:
                            sentence = "Nous sommes en mode {}, je passe donc en mode tempo jour".format(
                                runMode)
                        thermostat.setMode(32)

                    print "After action-> RunningMode: {} , runMode: {}".format(
                        thermostat.getRunningModeString(), thermostat.getModeString())

                else:
                    sentence = "Je n'ai pas compris s'il fait froid ou s'il fait chaud."

            else:
                sentence = "Je ne comprends pas l'action à effectuer avec le thermostat."

            print sentence
            hermes.publish_end_session(intent_message.session_id, sentence)
            return


with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(CONFIG_INI)

    except BaseException:
        config = None

    thermostat = None

    try:
        thermostat = open_thermostat(config)
        thermostat.read()

    except Exception as e:
        zibase = None
        print('Error Thermostat {}'.format(e))

    h.subscribe_intents(intent_received).start()
