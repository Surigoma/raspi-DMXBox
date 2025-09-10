from multiprocessing.connection import Connection
from typing import Any, Dict
from pythonosc.udp_client import SimpleUDPClient
from config import config
import time

format_str: Dict[str, str] = {
    "f": "",
    "t": ""
}
on_off: Dict[bool, Any] = {
    False: 0,
    True: 1
}
on_off_inverse: bool = False

micline = [1]

client:SimpleUDPClient = None

def logmsg(message): print("[osc] " + str(message))

def xor(a: bool, b: bool):
    return (a or b) and not (a and b)

def decode_message(message: Dict):
    global client, micline, format_str, on_off
    if not "method" in message:
        logmsg("Decode error. not found method.")
    elif message["method"] == "mute":
        for mic in micline:
            client.send_message(format_str["f"].format(mic), 0 if message["param"] == True else 1)
    pass

def start_osc(pipe: Connection, config: config):
    global client, micline, format_str, on_off, on_off_inverse
    c = config.config["osc"]
    ip = c["ip"] if "ip" in c else "192.168.2.48"
    port = c["port"] if "port" in c else 49900
    micline = c["mic"] if "mic" in c else [1]
    format_str["f"] = c["format"] if "format" in c else "/yosc:req/set/MIXER:Current/InCh/Fader/On/{}/1"
    format_str["t"] = c["type"] if "type" in c else "float"
    on_off_inverse = c["inverse"] if "inverse" in c else False
    if format_str["t"] == "int":
        on_off[xor(False, on_off_inverse)] = int(0)
        on_off[xor(True, on_off_inverse)] = int(1)
    elif format_str["t"] == "float":
        on_off[xor(False, on_off_inverse)] = float(0)
        on_off[xor(True, on_off_inverse)] = float(1)
    client = SimpleUDPClient(ip, port)
    logmsg("Start OSC service.")
    while not pipe.closed:
        if not pipe.poll():
            time.sleep(0.1)
            continue
        message = pipe.recv()
        logmsg(message)
        decode_message(message)