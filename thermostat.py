#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele (c)2014
# http://blog.onlinux.fr
#
#
# Import required Python libraries

import time
import logging
from Zapi import ZiBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s:%(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
class Constants:
    mode = {
        0: 'automatique',
        5: 'stop',
        6: 'hors gel',
        16: 'jour',
        32: 'tempo jour',
        48: 'nuit',
        64: 'tempo nuit'
    }

    runMode = {
        0: 'nuit',
        2: 'nuit',
        1: 'jour',
        3: 'jour'
    }

    state = {
        0: u'arrêt',
        1: u'marche'
    }

class Thermostat:
    'Common base class for Thermostat'
    def __init__(self, ip,
                 tempvariableid=28,
                 setpointdayvariableid=29,
                 setpointnightvariableid=30,
                 modevariableid=31,
                 statevariableid=13,
                 thermostatscenarioid=17,
                 thermostatprobeid=14):
        """ Indiquer l'adresse IP de la ZiBase """
        self.ip = ip
        self.tempVariableId = tempvariableid
        self.setpointDayVariableId = setpointdayvariableid
        self.setpointNightVariableId = setpointnightvariableid
        self.modeVariableId = modevariableid
        self.stateVariableId = statevariableid
        self.thermostatScenarioId = thermostatscenarioid
        self.thermostatProbeId = thermostatprobeid
        self.modeList = [0, 5, 6, 16, 32, 48, 64]
        self.state = None
        self.indoorTemp = None
        self.outdoorTemp = None
        self.runMode = None
        self.setpointDayValue = None
        self.setpointDay = None
        self.setpointNightValue = None
        self.setpointNight = None
        self.modeValue = None
        self.modeIndex = None
        self.title = 'Thermostat'
        self.zibase = ZiBase.ZiBase(ip)
        self.read()

    def __del__(self):
        class_name = self.__class__.__name__
        print class_name, "destroyed"

    def rotate(self, l, y=1):
        if len(l) == 0:
            return l
        y = y % len(l)

        return l[y:] + l[:y]

    def tempStr(self, value):
        if isinstance(value, int):
            temp = "{:d}".format(value)
        else:
            temp = "{:.1f}".format(value)
        #print value
        temp = temp + u'\N{DEGREE SIGN}' + 'C'
        return temp

    def search(self, list, key, value):
        for item in list:
            if item[key] == value:
                return item

    def read(self):
        start = time.time()
        zibase = self.zibase
        self.indoorTemp = self.getTemp()
        self.setpointDayValue = self.getSetpointDay()
        self.setpointNightValue = self.getSetpointNight()
        self.modeValue = self.getMode()
        probe = zibase.getSensorInfo('TT', str(self.thermostatProbeId))
        if probe:
            self.runMode = int(probe[2]) & 0x1
        else:
            logger.error(' Could not find any Thermostat with id TT {}'.format(
                self.thermostatProbeId))
            return
        v = zibase.getVariable(self.stateVariableId)
        if v >= 0:
            self.state = v & 0x01
        else:
            self.state = 0
        elapsed = (time.time() - start) * 1000
        logger.info(' indoorTemp[%d] setpointDay[%d] setpointNight[%d] runMode[%d][%s] state[%d][%s] runMode[%d][%s]' % (
        self.indoorTemp, self.setpointDayValue, self.setpointNightValue,
        self.modeValue, Constants.mode[self.modeValue], self.state,
        Constants.state[self.state], self.runMode, self.getRunModeString()))
        logger.debug(' retrieve data from %s in [%d ms]' % (self.ip, elapsed))

    def setVariable(self, variable, value):
        if variable < 52:
            start = time.time()
            self.zibase.setVariable(variable, value)
            elapsed = (time.time() - start) * 1000
            time.sleep(1)
            logger.debug(
                ' setVariable [%i] = %i  [%d ms]' %
                (int(variable), int(value), elapsed))
        else:
            logger.warning(
                ' setVariable  [%s]  cannot be > 52!' % (str(variable)))

    def setMode(self, mode=0):
        if mode in Constants.mode:
            self.modeValue = int(mode)
            self.setVariable(self.modeVariableId, int(mode))

            logger.debug(' Send mode %i [%s]  to %s ' % (
                int(mode), Constants.mode[self.modeValue], self.ip))
        else:
            logger.debug(
                ' Send mode %i  to %s . Error: invalid mode' %
                (int(mode), self.ip))

    def getStateString(self):
        return Constants.state[self.state]

    def getState(self):
        return self.state

    @property
    def mode(self):
        return self.zibase.getVariable(self.modeVariableId)

    def getMode(self):
        return self.zibase.getVariable(self.modeVariableId)

    def getModeString(self):
        return Constants.mode[self.getMode()]

    def getRunMode(self):
        return (self.runMode)

    def getRunModeString(self):
        if self.runMode is not None:
            return Constants.runMode[self.runMode]
        else:
            return None

    def setSetpointDay(self, value):
        value = int(value)
        if value > 230:
            value = 230
        self.setpointDayValue = value
        self.setVariable(self.setpointDayVariableId, value)
        logger.debug(' Send setpoindDay %i  to %s ' % (value, self.ip))
        # self.update()

    def getSetpointDay(self):
        return self.zibase.getVariable(self.setpointDayVariableId)

    def setSetpointNight(self, value):
        value = int(value)
        if value > 230:
            value = 230
        elif value < 140:
            value = 140

        self.setpointNightValue = value
        self.setVariable(self.setpointNightVariableId, value)
        logger.debug(' Send setpoindNight %i  to %s ' % (value, self.ip))
        # self.update()

    def getSetpointNight(self):
        return self.zibase.getVariable(self.setpointNightVariableId)

    def getTemp(self):
        return self.zibase.getVariable(self.tempVariableId)

    def addSetpointDay(self, incr=1):
        self.setpointDayValue += incr
        self.setSetpointDay(self.setpointDayValue)
        self.update()

    def addSetpointNight(self, incr=1):
        self.setpointNightValue += incr
        self.setSetpointNight(self.setpointNightValue)
        self.update()

    def update(self):
        self.zibase.runScenario(self.thermostatScenarioId)
        logger.debug(' Send force-update scenario %i  to %s ' %
                     (int(self.thermostatScenarioId), self.ip))
