from dmx import *
import time
import numpy as np
from config import config
from multiprocessing import Pipe
import json

def logmsg(message) : print("[dmx]" + message)

class ALLLIGHT(DMXDevice):
    channels = []
    fade = 0.0
    light = False
    start_time = 0
    end_time = 0
    priv_fade = 0

    def __init__(self, name):
        super().__init__(name, 1, num_chans=512)

    def addChannel(self, id):
        if id in self.channels:
            return
        self.channels.append(id)

    def fadeIn(self, interval=2.0, delay=1.0):
        self.light = True
        self.start_time = time.time() + delay
        self.end_time = self.start_time + interval
        self.priv_fade = self.fade

    def fadeOut(self, interval=2.0, delay=1.0):
        self.light = False
        self.start_time = time.time() + delay
        self.end_time = self.start_time + interval
        self.priv_fade = self.fade

    def update(self, dmx):
        if self.end_time == 0 or self.start_time == 0: return
        per = np.clip((time.time() - self.start_time) / (self.end_time - self.start_time), 0, 1)
        self.fade = np.clip(self.priv_fade + (per if self.light else -per), 0, 1)
        for i in self.channels:
            dmx.set_float(self.chan_no, i, self.fade)

dmx: DMXUniverse = None
fixture: ALLLIGHT = None
running = False

def decode_message(message):
    global dmx, fixture, running
    if not "method" in message:
        logmsg("Decode error. not found method.")
        return
    if message["method"] == "stop":
        running = False
        return
    if message["method"] == "fadeIn":
        fixture.fadeIn()
        return
    if message["method"] == "fadeOut":
        fixture.fadeOut()
        return
    pass

def start_dmx(pipe: Pipe, config: config):
    global dmx, fixture, running
    dmx = DMXUniverse(url=config.config["hw"]["url"] if config.config["hw"]["url"] else "ftdi://ftdi:232:AB0OXCQ4/1")
    fixture = ALLLIGHT("alllight")
    for i in range(1,4):
        fixture.addChannel(i)
    dmx.add_device(fixture)
    dmx.start_dmx_thread(1/30)
    running = True

    while running:
        if not pipe.poll():
            time.sleep(0.1)
            continue
        message = pipe.recv()
        logmsg(json.dumps(message))
        decode_message(message)
    logmsg ("Stopped DMX Process")
    pass