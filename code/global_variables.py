import configparser
import logging
from colorlog import ColoredFormatter

log_level = logging.DEBUG
log_format = (
    "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
)

logging.root.setLevel(log_level)
formatter = ColoredFormatter(log_format)

stream = logging.StreamHandler()
stream.setLevel(log_level)
stream.setFormatter(formatter)

LOG = logging.getLogger("pythonConfig")
LOG.setLevel(log_level)
LOG.addHandler(stream)

YES_VALUES = ["yes", "y", "true", "t", "1"]
NO_VALUES = ["no", "n", "false", "f", "0"]

try:
    with open("config.ini", "r") as f:
        file_contents = f.read()
except FileNotFoundError:
    config = configparser.ConfigParser()
    config["REQUIRED"] = {
        "BOT_TOKEN": "",
        "RADARR_HOST_URL": "http://",
        "RADARR_API_KEY": "",
        "ROOT_FOLDER_PATH": "",
        "QUALITY_PROFILE_ID": "",
        "ENABLE_JELLYFIN_TEMP_ACCOUNTS": "",
    }

    config["JELLYFIN_ACCOUNTS"] = {
        "JELLYFIN_URL": "",
        "JELLYFIN_API_KEY": "",
        "ACCOUNT_TIME": ""
    }

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    LOG.error("Configuration file `config.ini` has been generated. Please fill out all of the necessary information. Refer to the docs for information on what a specific configuration option is.")
    exit()

config = configparser.ConfigParser()
config.read_string(file_contents)

BOT_TOKEN = config["REQUIRED"]["BOT_TOKEN"]
RADARR_HOST_URL = config["REQUIRED"]["RADARR_HOST_URL"]
RADARR_API_KEY = config["REQUIRED"]["RADARR_API_KEY"]
ROOT_FOLDER_PATH = config["REQUIRED"]["ROOT_FOLDER_PATH"]
QUALITY_PROFILE_ID = config["REQUIRED"]["QUALITY_PROFILE_ID"]

if config["REQUIRED"]["ENABLE_JELLYFIN_TEMP_ACCOUNTS"].lower() in YES_VALUES:
    ENABLE_JELLYFIN_TEMP_ACCOUNTS = True
else:
    ENABLE_JELLYFIN_TEMP_ACCOUNTS = False

JELLYFIN_URL = config["JELLYFIN_ACCOUNTS"]["JELLYFIN_URL"]
JELLYFIN_API_KEY = config["JELLYFIN_ACCOUNTS"]["JELLYFIN_API_KEY"]
ACCOUNT_TIME = int(config["JELLYFIN_ACCOUNTS"]["ACCOUNT_TIME"])

RADARR_HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": RADARR_API_KEY
}

JELLYFIN_HEADERS = {
    "Content-Type": "application/json",
    "X-Emby-Token": JELLYFIN_API_KEY,
}
