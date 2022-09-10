#!/usr/bin/python
import uvicorn
from typing import List, Dict
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from config import config
from multiprocessing import Pipe
from util import *

app = FastAPI(title="Static")
api_app = FastAPI(title="REST API")

app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
pipe = None
config_data = None

ignoreRemote = False

@api_app.get("/fadeIn")
def get_fadeIn(interval:float = None, delay:float = None):
    global pipe
    message = {"method": "fadeIn", "param": {}}
    if interval != None:
        message["param"]["interval"] = interval
    if delay != None:
        message["param"]["delay"] = delay
    sendto_dmx(pipe, message)
    return {}

@api_app.get("/fadeOut")
def get_fadeOut(interval:float = None, delay:float = None):
    global pipe
    message = {"method": "fadeOut", "param": {}}
    if interval != None:
        message["param"]["interval"] = interval
    if delay != None:
        message["param"]["delay"] = delay
    sendto_dmx(pipe, message)
    return {}

@api_app.get("/fadeAddIn")
def get_fadeIn(interval:float = None, delay:float = None):
    global pipe
    message = {"method": "fadeAddIn", "param": {}}
    if interval != None:
        message["param"]["interval"] = interval
    if delay != None:
        message["param"]["delay"] = delay
    sendto_dmx(pipe, message)
    return {}

@api_app.get("/fadeAddOut")
def get_fadeOut(interval:float = None, delay:float = None):
    global pipe
    message = {"method": "fadeAddOut", "param": {}}
    if interval != None:
        message["param"]["interval"] = interval
    if delay != None:
        message["param"]["delay"] = delay
    sendto_dmx(pipe, message)
    return {}

@api_app.get("/mute")
def get_fadeOut(mute:bool = None):
    global pipe
    message = {"method": "mute", "param": mute}
    sendto_osc(pipe, message)
    return {}

@api_app.post("/config/setDefalutInterval")
def set_default_interval(interval: float = Form()):
    global pipe, config_data
    sendto_dmx(pipe, {"method": "setDefaultInterval", "param": interval})
    config_data.config["dmx"]["fadeInterval"] = interval
    return {}

@api_app.post("/config/setDefaultDelay")
def set_default_delay(delay: float = Form()):
    global pipe, config_data
    sendto_dmx(pipe, {"method": "setDefaultDelay", "param": delay})
    config_data.config["dmx"]["delay"] = delay
    return {}

class channels(BaseModel):
    channels: List[int]

@api_app.post("/config/setChannel")
def set_channels(channels: channels):
    global pipe, config_data
    sendto_dmx(pipe, {"method": "setChannel", "param": channels.channels})
    config_data.config["dmx"]["target_ch"] = channels.channels
    return {}

@api_app.post("/config/setAddChannel")
def set_channels(channels: channels):
    global pipe, config_data
    sendto_dmx(pipe, {"method": "setAddChannel", "param": channels.channels})
    config_data.config["dmx"]["target_additional_ch"] = channels.channels
    return {}

class fadeMaxs(BaseModel):
    fadeMaxs: Dict[str, int]

@api_app.post("/config/setTargetMax")
def set_channels(fadeMaxs: fadeMaxs):
    global pipe, config_data
    sendto_dmx(pipe, {"method": "setTargetMax", "param": fadeMaxs.fadeMaxs})
    config_data.config["dmx"]["target_max"] = fadeMaxs.fadeMaxs
    return {}

@api_app.post("/config/setIgnoreRemote")
def set_default_delay(flag: bool = Form()):
    global pipe, ignoreRemote
    sendto_main(pipe, {"method": "ignoreRemote", "param": flag})
    ignoreRemote = flag
    return {}

@api_app.get("/config/channels")
def get_channels():
    global config_data
    return config_data.config["dmx"]["target_ch"]

@api_app.get("/config/add_channels")
def get_channels():
    global config_data
    return config_data.config["dmx"]["target_additional_ch"]

@api_app.get("/config/interval")
def get_interval():
    global config_data
    return config_data.config["dmx"]["fadeInterval"]

@api_app.get("/config/delay")
def get_delay():
    global config_data
    return config_data.config["dmx"]["delay"]

@api_app.get("/config/target_max")
def get_target_max():
    global config_data
    return config_data.config["dmx"]["target_max"]

@api_app.get("/config/ignore_remote")
def get_target_max():
    global ignoreRemote
    return ignoreRemote

@api_app.post("/config/save")
def save_config():
    config_data.save()
    return {}

def start_restapi(pipe_c: Pipe, config: config):
    global pipe, config_data
    port = int(config.config["http"]["port"]) if "port" in config.config["http"] else 8888
    pipe = pipe_c
    config_data = config
    uvicorn.run(app=app, port=port, host="0.0.0.0")