import json

local_config = {}
config = {}
bot = None
queue = []
general = None
toad_info = None
toad_mode = False
honky_mode = False

def reload_config():
    global local_config
    global config
    local_config = json.loads(open(
        "local_config.json").read())  # Local config is config that should be kept different between each instance of the bot
    config = json.loads(
        open("config.json").read())
