from multiprocessing.connection import Connection
from typing import Dict
from pythonosc.udp_client import SimpleUDPClient
from config import config
import time

ip = "192.168.2.48"
port = 7001
micline = [1]

client:SimpleUDPClient = None

def logmsg(message): print("[osc] " + str(message))

def decode_message(message: Dict):
    global client, micline
    if not "method" in message:
        logmsg("Decode error. not found method.")
    elif message["method"] == "mute":
        for mic in micline:
            client.send_message("/yosc:req/set/MIXER:Current/InCh/Fader/On/{}/1".format(mic), 0 if message["param"] == True else 1)
    pass

def start_osc(pipe: Connection, config: config):
    global client, micline
    ip = config.config["osc"]["ip"] if "ip" in config.config["osc"] else "192.168.2.48"
    port = config.config["osc"]["port"] if "port" in config.config["osc"] else 49900
    micline = config.config["osc"]["mic"] if "mic" in config.config["osc"] else [1]
    client = SimpleUDPClient(ip, port)
    logmsg("Start OSC service.")
    while True:
        if not pipe.poll():
            time.sleep(0.1)
            continue
        message = pipe.recv()
        logmsg(message)
        decode_message(message)
    pass