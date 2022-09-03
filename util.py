def sendto_dmx(pipe, message):
    if pipe == None: return
    pipe.send({"to":"dmx", "body":message})

def sendto_serial(pipe, message):
    if pipe == None: return
    pipe.send({"to":"serial", "body":message})

def sendto_rest(pipe, message):
    if pipe == None: return
    pipe.send({"to":"rest", "body":message})

def sendto_main(pipe, message):
    if pipe == None: return
    pipe.send({"to":"main", "body":message})
