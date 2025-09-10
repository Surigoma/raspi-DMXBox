from multiprocessing.connection import Connection


def sendto_dmx(pipe: Connection, message):
    if pipe is None:
        return
    pipe.send({"to": "dmx", "body": message})


def sendto_serial(pipe: Connection, message):
    if pipe is None:
        return
    pipe.send({"to": "serial", "body": message})


def sendto_rest(pipe: Connection, message):
    if pipe is None:
        return
    pipe.send({"to": "rest", "body": message})


def sendto_main(pipe: Connection, message):
    if pipe is None:
        return
    pipe.send({"to": "main", "body": message})


def sendto_osc(pipe: Connection, message):
    if pipe is None:
        return
    pipe.send({"to": "osc", "body": message})
