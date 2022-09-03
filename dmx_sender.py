from dmx import *
import time
import numpy as np
from config import config
from multiprocessing import Pipe
import json

def logmsg(message) : print("[dmx]" + message)

class ALLLIGHT(DMXDevice):
    channels = []
    channel_max = {}
    fade = 0.0
    light = False
    start_time = 0
    end_time = 0
    priv_fade = 0
    interval = 2
    delay = 0

    def __init__(self, name):
        super().__init__(name, 1, num_chans=512)

    def addChannel(self, id):
        if id in self.channels:
            return
        self.channels.append(id)

    def fadeIn(self, interval=None, delay=None):
        interval = interval if interval != None else self.interval
        delay = delay if delay != None else self.delay
        self.light = True
        self.start_time = time.time() + delay
        self.end_time = self.start_time + interval
        self.priv_fade = self.fade

    def fadeOut(self, interval=None, delay=None):
        interval = interval if interval != None else self.interval
        delay = delay if delay != None else self.delay
        self.light = False
        self.start_time = time.time() + delay
        self.end_time = self.start_time + interval
        self.priv_fade = self.fade

    def setDefaultInterval(self, interval):
        self.interval = interval
        return

    def setDefaultDelay(self, delay):
        self.delay = delay
        return

    def update(self, dmx):
        if self.end_time == 0 or self.start_time == 0: return
        per = 1 if self.start_time < time.time() else 0
        if (self.end_time - self.start_time) > 0:
            per = np.clip((time.time() - self.start_time) / (self.end_time - self.start_time), 0.0, 1.0)
        self.fade = np.clip(self.priv_fade + (per if self.light else -per), 0.0, 1.0)
        for i in self.channels:
            max = self.channel_max[str(i)] if str(i) in self.channel_max else 255
            max = max if max > 0 else 1
            dmx.set_float(self.chan_no, i, self.fade, 0, max)

    def updateChannel(self, channels):
        self.channels.clear()
        for c in channels:
            if c >= 1 and c <= 512:
                self.channels.append(c)

    def updateChannelMax(self, fadeMaxs):
        self.channel_max.clear()
        for k, v in fadeMaxs.items():
            k_i = int(k)
            if k_i >= 1 and k_i <= 512:
                self.channel_max[k] = v

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
    elif message["method"] == "setTargetMax":
        if not "param" in message:
            return
        fixture.updateChannelMax(message["param"])
    pass

def start_dmx(pipe: Pipe, config: config):
    global dmx, fixture, running
    dmx = DMXUniverse(url=config.config["hw"]["url"] if config.config["hw"]["url"] else "ftdi://ftdi:232:AB0OXCQ4/1")
    fixture = ALLLIGHT("alllight")
    if "target_ch" in config.config["dmx"]:
        for i in config.config["dmx"]["target_ch"]:
            fixture.addChannel(i)
    if "target_max" in config.config["dmx"]:
        for k, v in config.config["dmx"]["target_max"].items():
            fixture.channel_max[k] = v
    if "preStatus" in config.config["dmx"]:
        if config.config["dmx"]["preStatus"]:
            fixture.fadeIn(0, 0)
        else:
            fixture.fadeOut(0, 0)
    fixture.interval = config.config["dmx"]["interval"] if "interval" in config.config["dmx"] else 2.0
    fixture.delay = config.config["dmx"]["delay"] if "delay" in config.config["dmx"] else 0.0
    fps = config.config["dmx"]["fps"] if "fps" in config.config["dmx"] else 30
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
    pass