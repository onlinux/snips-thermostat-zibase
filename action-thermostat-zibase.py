#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#
#
# Import required Python libraries
import os
import logging
import logging.config
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
THERMOSTATTURNOFF = 'ericvde31830:thermostatTurnOff'
THERMOSTATMODE = 'ericvde31830:thermostatMode'

# os.path.realpath returns the canonical path of the specified filename,
# eliminating any symbolic links encountered in the path.
path = os.path.dirname(os.path.realpath(sys.argv[0]))
configPath = path + '/' + CONFIG_INI

logging.config.fileConfig(configPath)
logger = logging.getLogger(__name__)


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

    logger.debug(" Address ip zibase:{}".format(ip))
    logger.debug(" Indoor Temperature:{}".format(
        thermostat.tempStr(thermostat.getTemp() / 10.0)))
    logger.debug(" Thermostat Mode:{}".format(thermostat.getModeString()))
    logger.debug(" Thermostat State:{}".format(thermostat.getStateString()))
    logger.debug(" Thermostat runMode:{}".format(
        thermostat.getRunModeString()))
    logger.debug(" setpoint Day:  {}°C".format(
        thermostat.getSetpointDay() / 10.0))
    logger.debug(" setpoint Night:{}°C".format(
        thermostat.getSetpointNight() / 10.0))
    return thermostat


def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    logger.debug(intentName)

    for (slot_value, slot) in intent_message.slots.items():
        logger.debug('Slot {} -> \n\tRaw: {} \tValue: {}'
                     .format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))

    if intentName == THERMOSTATMODE:
        thermostat.read()
        logger.debug("Change thermostat mode")
        if intent_message.slots.thermostat_mode:
            tmode = intent_message.slots.thermostat_mode.first().value
            logger.debug(
                "Je dois passer le thermostat en mode {}".format(tmode))
            sentence = "OK, je passe le thermostat en mode {}".format(tmode)

            # Invert Thermostat.mode dict first
            inv_mode = {value: key for key, value in Thermostat.mode.items()}
            logger.debug(inv_mode)
            if tmode in inv_mode:
                thermostat.setMode(inv_mode[tmode])
                thermostat.update()

            else:
                sentence = 'Désolée mais je ne connais pas le mode {}'.format(
                    tmode)

            hermes.publish_end_session(intent_message.session_id, sentence)
            return

    if intentName == THERMOSTATTURNOFF:
        thermostat.read()
        logger.debug("Thermostat turnOff")
        if intent_message.slots.temperature_device:
            thermostat.setMode(48)  # Turn nightMode on
            sentence = "Ok, je passe en mode nuit."
            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)
            return

    if intentName == THERMOSTATSET:
        logger.debug("Thermostat Set")
        thermostat.read()
        if intent_message.slots.temperature_decimal:
            temperature = intent_message.slots.temperature_decimal.first().value
            logger.debug("Température reconnue:".format, (temperature))
            runMode = thermostat.getRunModeString()
            mode = thermostat.getModeString()

            if runMode == 'nuit' and 'jour' not in mode:
                thermostat.setSetpointNight(int(temperature))
                sentence = "Ok, je passe la consigne de {} à {} degrés".format(
                    runMode, str(temperature / 10.0))
            elif runMode == 'jour' and 'nuit' not in mode:
                thermostat.setSetpointDay(int(temperature))
                sentence = "Ok, je passe la consigne de {} à {} degrés".format(
                    runMode, str(temperature / 10.0))
            else:
                sentence = "Désolée mais je ne sais pas quelle consigne changer car le mode est {}".format(
                    mode)

            thermostat.update()
            hermes.publish_end_session(intent_message.session_id, sentence)
            return

    if intentName == THERMOSTATSHIFT:
        if intent_message.slots.up_down:
            up_down = intent_message.slots.up_down.first().value
            action = up_down.encode('utf-8')

            if action is not None:

                setPoint = None
                runMode = thermostat.getRunModeString()
                mode = thermostat.getModeString()
                logger.debug("runMode: {}, Mode: {}".format(
                    runMode, mode
                ))
                if mode == 'stop' or mode == 'hors gel':
                    sentence = "Désolée mais nous sommes en mode {}. Je ne fais rien dans ce cas.".format(
                        mode)
                elif action == 'down':
                    if runMode == 'jour' or 'jour' in mode:
                        thermostat.addSetpointDay(-1)
                        setPoint = str(thermostat.getSetpointDay()
                                       / 10.0).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je descends donc la consigne de jour à {} degrés.".format(
                            mode, setPoint)
                    else:
                        thermostat.addSetpointNight(-1)
                        setPoint = str(thermostat.getSetpointNight()
                                       / 10.0).replace('.', ',')
                        sentence = "Nous sommes en mode {} économique, je descends donc la consigne de nuit à {} degrés.".format(
                            mode, setPoint)

                elif action == "up":
                    if 'nuit' not in mode and runMode == 'jour' or 'jour' in mode:
                        thermostat.addSetpointDay(1)
                        setPoint = str(thermostat.getSetpointDay()
                                       / 10.0).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je monte la consigne de jour à {} degrés.".format(
                            mode, setPoint)
                    else:
                        # switch to mode tempo-jour
                        if runMode == 'nuit' and mode == 'automatique':
                            sentence = "Nous sommes en mode {} économique, je passe donc en mode tempo jour".format(
                                mode)
                        else:
                            sentence = "Nous sommes en mode {}, je passe donc en mode tempo jour".format(
                                mode)
                        thermostat.setMode(32)

                    logger.debug("After action-> runMode: {} , mode: {}".format(
                        thermostat.getRunModeString(), thermostat.getModeString()))

                else:
                    sentence = "Je n'ai pas compris s'il fait froid ou s'il fait chaud."

            else:
                sentence = "Je ne comprends pas l'action à effectuer avec le thermostat."

            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)
            return


with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(configPath)

    except BaseException:
        config = None

    thermostat = None

    try:
        thermostat = open_thermostat(config)
        logger.info('Thermostat initialization: OK')

    except Exception as e:
        zibase = None
        logger.error('Error Thermostat {}'.format(e))

    h.subscribe_intents(intent_received).start()
