#!/usr/bin/python
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from config import config
from multiprocessing import Pipe

app = FastAPI(title="Static")
api_app = FastAPI(title="REST API")

app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
pipe = None
config_data = None

def sendto_dmx(message):
    global pipe
    if pipe == None: return
    pipe.send({"to":"dmx", "body":message})

def sendto_serial(message):
    global pipe
    if pipe == None: return
    pipe.send({"to":"serial", "body":message})

@api_app.get("/fadeIn")
def get_fadeIn(interval:float = None, delay:float = None):
    message = {"method": "fadeIn", "param": {}}
    if interval != None:
        message["param"]["interval"] = interval
    if delay != None:
        message["param"]["delay"] = delay
    sendto_dmx(message)
    return {}

@api_app.get("/fadeOut")
def get_fadeOut(interval:float = None, delay:float = None):
    message = {"method": "fadeOut", "param": {}}
    if interval != None:
        message["param"]["interval"] = interval
    if delay != None:
        message["param"]["delay"] = delay
    sendto_dmx(message)
    return {}

@api_app.post("/config/setDefalutInterval")
def set_default_interval(interval: float):
    sendto_dmx({"method": "setDefaultInterval", "param": interval})
    return {}

@api_app.post("/config/setDefaultDelay")
def set_default_delay(delay: float):
    sendto_dmx({"method": "setDefaultDelay", "param": delay})
    return {}

@api_app.post("/config/save")
def set_default_delay(delay: float):
    config_data.save()
    return {}

def start_restapi(pipe_c: Pipe, config: config):
    global pipe, config_data
    port = int(config.config["http"]["port"]) if "port" in config.config["http"] else 8888
    pipe = pipe_c
    config_data = config
    uvicorn.run(app=app, port=port, host="0.0.0.0")