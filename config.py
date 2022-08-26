import json

class config:
    config = {}
    def __init__(self, path = "./config.json"):
        with open(path, mode="r") as f:
            self.config = json.load(f)

    def save(self, path = "./config.json"):
        with open(path, mode="w") as f:
            f.write(json.dumps(self.config))
