import json
import os.path
import pickle
import time

local_config = {}
config = {}
bot = None
queue = []
general = None
vc_text = None
toad_info = None
toad_mode = False
honky_mode = False
save_data = {}


def save_save_data():
    with open(config["save_data_dir"], "wb") as f:
        pickle.dump(save_data, f)


def load_save_data():
    global save_data
    if not os.path.isfile(config["save_data_dir"]):
        save_data = {}
        return
    with open(config["save_data_dir"], "rb") as f:
        save_data = pickle.load(f)


def reload_config():
    global local_config
    global config
    local_config = json.loads(open(
        "local_config.json").read())  # Local config is config that should be kept different between each instance of the bot
    config = json.loads(
        open("config.json").read())


def fix_data():
    if "last_birthday_wish" not in save_data:
        save_data["last_birthday_wish"] = time.time()
