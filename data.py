import json

local_config = {}
config = {}
bot = None
queue = []
general = None
toad_info = None


def reload_config():
    global local_config
    global config
    local_config = json.loads(open(
        "local_config.json").read())  # Local config is config that should be kept different between each instance of the bot
    config = json.loads(
        open("config.json").read())
