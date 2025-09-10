#!/usr/bin/python
from multiprocessing.connection import Connection
from typing import Callable, Dict
from rest_api import start_restapi
from dmx_sender import start_dmx
from serial_port import start_serial
from tcp_server import start_tcp
from osc_service import start_osc
from multiprocessing import Process, Pipe
from config import config
import json
import time
from util import *

def logmsg(message): print("[main]" + message)

pipe_table: Dict[str, Connection] = {
    "dmx": None,
    "rest": None,
    "serial": None,
    "tcp": None,
    "osc": None,
}
process_table: Dict[str, Process] = {
    "dmx": None,
    "rest": None,
    "serial": None,
    "tcp": None,
    "osc": None,
}

ignoreRemote = False
running = True

def transportMessage(message: Dict[str, Dict]):
    global pipe_table
    if not "to" in message and "body" in message:
        logmsg("unknown message." + json.dumps(message))
    elif message["to"] in pipe_table and pipe_table[message["to"]] is not None:
        pipe_table[message["to"]].send(message["body"])
    elif message["to"] == "main":
        if message["body"]["method"] == "ignoreRemote":
            ignoreRemote = bool(message["body"]["param"])
            logmsg("ignore Remote :" + str(ignoreRemote) + " " + str(message["body"]["param"]))
    return

def register_pipelines(name: str, target: Callable[[Connection, config], None], config: config):
    global process_table, pipe_table
    p, c = Pipe()
    pipe_table[name] = p
    process_table[name] = Process(target=target, args=(c, config, ))

if __name__ == '__main__':
    config_data = config()

    register_pipelines("dmx", start_dmx, config_data) # Create DMX process server
    register_pipelines("rest", start_restapi, config_data) # Create REST API and static file server
    # register_pipelines("serial", start_serial, config_data)
    register_pipelines("tcp", start_tcp, config_data)
    register_pipelines("osc", start_osc, config_data)

    for k, v in process_table.items():
        if v is not None:
            v.start()

    while running:
        try:
            for k, v in pipe_table.items():
                if isinstance(v, Connection):
                    if v.poll():
                        transportMessage(v.recv())
        except KeyboardInterrupt:
            running = False
        time.sleep(0.01)

    for k, v in pipe_table.items():
        if isinstance(v, Connection):
            v.close()

    for k, v in process_table.items():
        if v is not None:
            v.join()
