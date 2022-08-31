from tokenize import String
import serial
from config import config
from multiprocessing import Pipe
from util import *
import time

def logmsg(message) : print("[serial]" + message)

pipe: Pipe = None

def start_serial(pipe_c: Pipe, config:config):
    pipe = pipe_c
    dev = config.config["serial"]["dev"] if "dev" in config.config["serial"] else "/dev/vmodem0"
    baudrate = config.config["serial"]["speed"] if "speed" in config.config["serial"] else 115200
    for i in range(0, 100):
        try:
            logmsg("Open serial port. " + dev + ":" + str(baudrate))
            with serial.Serial(dev, baudrate, timeout=1) as s:
                i = 0
                while True:
                    text = s.readline()
                    if text == b"":
                        continue
                    try:
                        text_s = text.decode("utf-8").strip()
                    except UnicodeDecodeError:
                        continue
                    logmsg("msg:" + str(text_s))
                    if text_s == "fi":
                        sendto_dmx(pipe, {"method": "fadeIn"})
                    elif text_s == "fo":
                        sendto_dmx(pipe, {"method": "fadeOut"})
        except serial.SerialException:
            logmsg("Close or broken serial port. Retry connection.(" + str(i) +")")
            time.sleep(3)
            pass