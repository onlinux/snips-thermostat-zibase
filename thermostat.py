#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele (c)2014
# http://blog.onlinux.fr
#
#   __     _                             _                    _            _
#  /__\ __(_) ___  /\   /\__ _ _ __   __| | ___  ___ __ _ ___| |_ ___  ___| | ___
# /_\| '__| |/ __| \ \ / / _` | '_ \ / _` |/ _ \/ __/ _` / __| __/ _ \/ _ \ |/ _ \
# //__| |  | | (__   \ V / (_| | | | | (_| |  __/ (_| (_| \__ \ ||  __/  __/ |  __/
# \__/|_|  |_|\___|   \_/ \__,_|_| |_|\__,_|\___|\___\__,_|___/\__\___|\___|_|\___|
#
#
# Import required Python libraries

import time
import logging
from Zapi import ZiBase


class Thermostat:
    'Common base class for thermostat'

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

    def __init__(self, ip,
                 tempVariableId=28,
                 setpointDayVariableId=29,
                 setpointNightVariableId=30,
                 modeVariableId=31,
                 stateVariableId=13,
                 thermostatScenarioId=32):
        """ Indiquer l'adresse IP de la ZiBase """
        self.ip = ip
        self.tempVariableId = tempVariableId
        self.setpointDayVariableId = setpointDayVariableId
        self.setpointNightVariableId = setpointNightVariableId
        self.modeVariableId = modeVariableId
        self.stateVariableId = stateVariableId
        self.thermostatScenarioId = thermostatScenarioId
        self.modeList = [0, 5, 6, 16, 32, 48, 64]
        self.state = None
        self.indoorTemp = None
        self.outdoorTemp = None
        self.runningMode = None
        self.setpointDayValue = None
        self.setpointDay = None
        self.setpointNightValue = None
        self.setpointNight = None
        self.modeValue = None
        self.modeIndex = None
        self.title = 'Thermostat'
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s',
            filename='./thermostat.log',
            level=logging.DEBUG)

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

        v = zibase.getVariable(self.stateVariableId)
        if v >= 0:
            self.state = v & 0x01
        else:
            self.state = 0

        elapsed = (time.time() - start) * 1000
        logging.debug(' indoorTemp [%d] setpointDay [%d] setpointNight [%d] mode [%d] [%s] state [%d] [%s]' % (
            self.indoorTemp, self.setpointDayValue, self.setpointNightValue, self.modeValue, Thermostat.mode[self.modeValue], self.state, Thermostat.state[self.state]))
        logging.debug(' retrieve data from %s in [%d ms]' % (self.ip, elapsed))

    def setVariable(self, variable, value):
        if variable < 52:
            start = time.time()
            self.zibase.setVariable(variable, value)
            elapsed = (time.time() - start) * 1000
            time.sleep(1)
            logging.debug(
                ' setVariable [%i] = %i  [%d ms]' %
                (int(variable), int(value), elapsed))
        else:
            logging.warning(' setVariable  [%s]  is not int' % (str(variable)))

    def setMode(self, mode=0):
        if mode in Thermostat.mode:
            self.modeValue = int(mode)
            self.setVariable(self.modeVariableId, int(mode))

            logging.debug(' Send mode %i [%s]  to %s ' % (
                int(mode), Thermostat.mode[self.modeValue], self.ip))
        else:
            logging.debug(
                ' Send mode %i  to %s . Error: invalid mode' %
                (int(mode), self.ip))

    def getMode(self):
        return self.zibase.getVariable(self.modeVariableId)

    def getModeString(self):
        return Thermostat.mode[self.getMode()]

    def setSetpointDay(self, value):
        value = int(value)
        if value > 230:
            value = 230
        self.setpointDayValue = value
        self.setVariable(self.setpointDayVariableId, value)
        logging.debug(' Send setpoindDay %i  to %s ' % (value, self.ip))

    def getSetpointDay(self):
        return self.zibase.getVariable(self.setpointDayVariableId)

    def setSetpointNight(self, value):
        value = int(value)
        if value > 230:
            value = 230
        self.setpointNightValue = value
        self.setVariable(self.setpointNightVariableId, value)
        logging.debug(' Send setpoindNight %i  to %s ' % (value, self.ip))

    def getSetpointNight(self):
        return self.zibase.getVariable(self.setpointNightVariableId)

    def getTemp(self):
        return self.zibase.getVariable(self.tempVariableId)

    def addSetpointDay(self, incr=1):
        self.setpointDayValue += incr
        self.setSetpointDay(self.setpointDayValue)

    def addSetpointNight(self, incr=1):
        self.setpointNightValue += incr
        self.setSetpointNight(self.setpointNightValue)

    def update(self):
        self.zibase.runScenario(self.thermostatScenarioId)
        logging.debug(' Send force-update scenario %i  to %s ' %
                      (int(self.thermostatScenarioId), self.ip))
