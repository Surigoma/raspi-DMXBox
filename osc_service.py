from pythonosc.udp_client import SimpleUDPClient
from config import config
from multiprocessing import Pipe
import time

ip = "192.168.2.48"
port = 7001
micline = 1

client:SimpleUDPClient = None

def logmsg(message): print("[osc] " + str(message))

def decode_message(message):
    global client, micline
    if not "method" in message:
        logmsg("Decode error. not found method.")
    elif message["method"] == "mute":
        client.send_message("/1/mute/1/" + str(micline), 1.0 if message["param"] == True else 0.0)
    pass

def start_osc(pipe: Pipe, config:config):
    global client, micline
    ip = config.config["osc"]["ip"] if "ip" in config.config["osc"] else "192.168.2.48"
    port = config.config["osc"]["port"] if "port" in config.config["osc"] else 7001
    micline = config.config["osc"]["mic"] if "mic" in config.config["osc"] else 1
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