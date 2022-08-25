#!/usr/bin/python
import uvicorn
from fastapi import FastAPI
from config import config
from multiprocessing import Pipe

app = FastAPI()
pipe = None

def sendto_dmx(message):
    global pipe
    if pipe == None: return
    pipe.send({"to":"dmx", "body":message})

def sendto_serial(message):
    global pipe
    if pipe == None: return
    pipe.send({"to":"serial", "body":message})

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/fadeIn")
def get_fadeIn():
    sendto_dmx({"method": "fadeIn"})
    return {}

@app.get("/api/fadeOut")
def get_fadeOut():
    sendto_dmx({"method": "fadeOut"})
    return {}

def start_restapi(pipe_c: Pipe, config: config):
    global pipe
    port = int(config.config["http"]["port"]) if "port" in config.config["http"] else 8888
    pipe = pipe_c
    uvicorn.run(app=app, port=port, host="0.0.0.0")