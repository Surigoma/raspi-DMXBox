#!/usr/bin/python
from rest_api import start_restapi
from dmx_sender import start_dmx
from serial_port import start_serial
from tcp_server import start_tcp
from multiprocessing import Process, Pipe, Array
from config import config
import json
import time
from util import *

def logmsg(message): print("[main]" + message)

pipe_dmx_p = None
pipe_rest_p = None
pipe_serial_p = None
pipe_tcp_p = None

def transportMessage(message):
    global pipe_dmx_p, pipe_rest_p, pipe_serial_p, pipe_tcp_p
    if not "to" in message and "body" in message:
        logmsg("unknown message." + json.dumps(message))
    elif pipe_dmx_p != None and message["to"] == "dmx":
        pipe_dmx_p.send(message["body"])
    elif pipe_rest_p != None and message["to"] == "rest":
        pipe_rest_p.send(message["body"])
    elif pipe_serial_p != None and message["to"] == "serial":
        pipe_serial_p.send(message["body"])
    elif pipe_tcp_p != None and message["to"] == "tcp":
        pipe_tcp_p.send(message["body"])
    return

if __name__ == '__main__':
    config_data = config()

    # Create DMX process server
    pipe_dmx_p, pipe_dmx_c = Pipe()
    p_dmx = Process(target=start_dmx, args=(pipe_dmx_c, config_data, ))

    # Create REST API and static file server
    pipe_rest_p, pipe_rest_c = Pipe()
    p_rest = Process(target=start_restapi, args=(pipe_rest_c, config_data, ))

    pipe_serial_p, pipe_serial_c = Pipe()
    p_serial = Process(target=start_serial, args=(pipe_serial_c, config_data, ))

    pipe_tcp_p, pipe_tcp_c = Pipe()
    p_tcp = Process(target=start_tcp, args=(pipe_tcp_c, config_data, ))

    p_dmx.start()
    p_rest.start()
    p_serial.start()
    p_tcp.start()
    running = True

    while running:
        if pipe_rest_p.poll():
            message = pipe_rest_p.recv()
            transportMessage(message)
        if pipe_dmx_p.poll():
            message = pipe_dmx_p.recv()
            transportMessage(message)
        if pipe_serial_p.poll():
            message = pipe_serial_p.recv()
            transportMessage(message)
        if pipe_tcp_p.poll():
            message = pipe_tcp_p.recv()
            transportMessage(message)
        time.sleep(0.01)

    p_dmx.join()
    p_rest.join()
    p_serial.join()
    p_tcp.join()
    
    pipe_dmx_p.close()
    pipe_rest_p.close()
    pipe_serial_p.close()
    pipe_tcp_p.close()
