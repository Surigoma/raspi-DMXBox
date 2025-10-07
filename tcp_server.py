import socket
from config import config
from multiprocessing.connection import Connection
from util import *

listen_backlog = 5
recv_buffer = 128

def logmsg(message) : print("[tcp]" + message)

def start_tcp(pipe: Connection, config:config):
    server_ip = config.config["tcp"]["ip"] if "ip" in config.config["tcp"] else "0.0.0.0"
    server_port = config.config["tcp"]["port"] if "ip" in config.config["tcp"] else "50000"
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind((server_ip, server_port))
    tcp_server.listen(listen_backlog)
    tcp_server.settimeout(1.0)
    logmsg("listen start. " + server_ip + ":" + str(server_port))
    while not pipe.closed:
        try:
            client, address = tcp_server.accept()
        except TimeoutError:
            continue
        logmsg("connect. " + str(address))
        data = client.recv(recv_buffer)
        logmsg("msg:" + str(data))
        if data == b"":
            client.close()
            continue
        try:
            data_s = data.decode("utf-8").splitlines()
        except UnicodeDecodeError:
            client.close()
            continue
        logmsg("msg:" + str(data_s))
        for cmd in data_s:
            if cmd == "fi":
                sendto_dmx(pipe, {"method": "fadeIn"})
            elif cmd == "fo":
                sendto_dmx(pipe, {"method": "fadeOut"})
            elif cmd == "fai":
                sendto_dmx(pipe, {"method": "fadeAddIn"})
            elif cmd == "fao":
                sendto_dmx(pipe, {"method": "fadeAddOut"})
            elif cmd == "ci":
                sendto_dmx(pipe, {"method": "fadeIn", "param":{"interval":0}})
            elif cmd == "co":
                sendto_dmx(pipe, {"method": "fadeOut", "param":{"interval":0}})
            elif cmd == "mute":
                sendto_osc(pipe, {"method": "mute", "param": True})
            elif cmd == "unmute":
                sendto_osc(pipe, {"method": "mute", "param": False})
        client.send("ack".encode("utf-8"))
        client.close()
    pass