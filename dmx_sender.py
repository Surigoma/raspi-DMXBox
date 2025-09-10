from multiprocessing.connection import Connection
from typing import Dict
from dmx import *
import time
import numpy as np
from config import config
import json

def logmsg(message) : print("[dmx]" + message)

class timeitem():
    channel: int = 0
    fademax: int = 255
    light = False
    start_time = time.time()
    end_time = start_time
    interval: float = 2.0
    delay: float = 0.0
    priv_fade: float = 0.0
    fade: float = 0.0

    def updateTime(self, interval, delay):
        interval = interval if interval != None else self.interval
        delay = delay if delay != None else self.delay
        self.start_time = time.time() + delay
        self.end_time = self.start_time + interval
        self.priv_fade = self.fade

    def fadeIn(self, interval = None, delay = None):
        self.light = True
        self.updateTime(interval, delay)

    def fadeOut(self, interval = None, delay = None):
        self.light = False
        self.updateTime(interval, delay)
    
    def update(self, dmx: DMXUniverse):
        if self.end_time == 0 or self.start_time == 0: return
        per = 1 if self.start_time < time.time() else 0
        if (self.end_time - self.start_time) > 0:
            per = np.clip((time.time() - self.start_time) / (self.end_time - self.start_time), 0.0, 1.0)
        self.fade = np.clip(self.priv_fade + (per if self.light else -per), 0.0, 1.0)
        max = self.fademax if not (self.fademax == None) else 255
        max = max if max > 0 else 1
        dmx.set_float(self.channel, 1, self.fade, 0, max)
        pass

class ALLLIGHT(DMXDevice):
    channels: Dict[str, timeitem] = {}
    additional_channel: Dict[str, timeitem] = {}
    interval = 0
    delay = 0

    def __init__(self, name):
        super().__init__(name, 1, num_chans=512)

    def addChannel(self, id, interval = None, delay = None):
        if id in self.channels:
            return
        if not (id >= 1 and id <= 512):
            return
        channel = timeitem()
        channel.channel = id
        channel.interval = interval if interval != None else self.interval
        channel.delay = delay if delay != None else self.delay
        self.channels[str(id)] = channel

    def addAdditionalChannel(self, id, interval = None, delay = None):
        if id in self.additional_channel:
            return
        if not (id >= 1 and id <= 512):
            return
        channel = timeitem()
        channel.channel = id
        channel.interval = interval if interval != None else self.interval
        channel.delay = delay if delay != None else self.delay
        self.additional_channel[str(id)] = channel

    def fadeIn(self, interval=None, delay=None):
        for _, v in self.channels.items():
            v.fadeIn(interval, delay)

    def fadeOut(self, interval=None, delay=None):
        for _, v in self.channels.items():
            v.fadeOut(interval, delay)

    def fadeAddIn(self, interval=None, delay=None):
        for _, v in self.additional_channel.items():
            v.fadeIn(interval, delay)

    def fadeAddOut(self, interval=None, delay=None):
        for _, v in self.additional_channel.items():
            v.fadeOut(interval, delay)

    def setDefaultInterval(self, interval: float):
        for _, v in self.channels.items():
            v.interval = interval
        for _, v in self.additional_channel.items():
            v.interval = interval
        return

    def setDefaultDelay(self, delay: float):
        for _, v in self.channels.items():
            v.delay = delay
        for _, v in self.additional_channel.items():
            v.delay = delay
        return

    def update(self, dmx: DMXUniverse):
        for _, v in self.channels.items():
            v.update(dmx)
        for _, v in self.additional_channel.items():
            v.update(dmx)

    def updateChannel(self, channels):
        self.channels.clear()
        for c in channels: 
            self.addChannel(c)

    def updateAddChannel(self, channels):
        self.channels.clear()
        for c in channels: 
            self.addAdditionalChannel(c)

    def updateChannelMax(self, fadeMaxs: Dict[str, int]):
        for k, v in fadeMaxs.items():
            if k in self.channels:
                self.channels[k].fademax = v
            if k in self.additional_channel:
                self.additional_channel[k].fademax = v

dmx: DMXUniverse = None
fixture: ALLLIGHT = None
running = False

def decode_message(message):
    global dmx, fixture, running
    if not "method" in message:
        logmsg("Decode error. not found method.")
    elif message["method"] == "stop":
        running = False
    elif message["method"] == "fadeIn":
        interval = None
        delay = None
        if "param" in message:
            if "interval" in message["param"]:
                interval = message["param"]["interval"]
            if "delay" in message["param"]:
                delay = message["param"]["delay"]
        fixture.fadeIn(interval, delay)
    elif message["method"] == "fadeOut":
        interval = None
        delay = None
        if "param" in message:
            if "interval" in message["param"]:
                interval = message["param"]["interval"]
            if "delay" in message["param"]:
                delay = message["param"]["delay"]
        fixture.fadeOut(interval, delay)
    elif message["method"] == "fadeAddIn":
        interval = None
        delay = None
        if "param" in message:
            if "interval" in message["param"]:
                interval = message["param"]["interval"]
            if "delay" in message["param"]:
                delay = message["param"]["delay"]
        fixture.fadeAddIn(interval, delay)
    elif message["method"] == "fadeAddOut":
        interval = None
        delay = None
        if "param" in message:
            if "interval" in message["param"]:
                interval = message["param"]["interval"]
            if "delay" in message["param"]:
                delay = message["param"]["delay"]
        fixture.fadeAddOut(interval, delay)
    elif message["method"] == "updateChannel":
        if not "param" in message:
            return
        fixture.updateChannel(message["param"])
    elif message["method"] == "setDefaultInterval":
        if not "param" in message:
            return
        fixture.setDefaultInterval(message["param"])
    elif message["method"] == "setDefaultDelay":
        if not "param" in message:
            return
        fixture.setDefaultDelay(message["param"])
    elif message["method"] == "setChannel":
        if not "param" in message:
            return
        fixture.updateChannel(message["param"])
    elif message["method"] == "setAddChannel":
        if not "param" in message:
            return
        fixture.updateAddChannel(message["param"])
    elif message["method"] == "setTargetMax":
        if not "param" in message:
            return
        fixture.updateChannelMax(message["param"])

def start_dmx(pipe: Connection, config: config):
    global dmx, fixture, running
    dmx = DMXUniverse(url=config.config["hw"]["url"] if config.config["hw"]["url"] else "ftdi://ftdi:232:AB0OXCQ4/1")
    fixture = ALLLIGHT("alllight")
    fixture.interval = config.config["dmx"]["fadeInterval"] if "fadeInterval" in config.config["dmx"] else 2.0
    fixture.delay = config.config["dmx"]["delay"] if "delay" in config.config["dmx"] else 0.0
    if "target_ch" in config.config["dmx"]:
        for i in config.config["dmx"]["target_ch"]:
            fixture.addChannel(i)
    if "target_additional_ch" in config.config["dmx"]:
        for i in config.config["dmx"]["target_additional_ch"]:
            fixture.addAdditionalChannel(i)
    if "target_max" in config.config["dmx"]:
        fixture.updateChannelMax(config.config["dmx"]["target_max"])
    if "preStatus" in config.config["dmx"]:
        if config.config["dmx"]["preStatus"]:
            fixture.fadeIn(0, 0)
        else:
            fixture.fadeOut(0, 0)
    fps: float = config.config["dmx"]["fps"] if "fps" in config.config["dmx"] else 30
    dmx.add_device(fixture)
    dmx.start_dmx_thread(1/fps)
    running = True

    while running:
        if not pipe.poll():
            time.sleep(0.01)
            continue
        message = pipe.recv()
        logmsg(json.dumps(message))
        decode_message(message)
    logmsg ("Stopped DMX Process")
