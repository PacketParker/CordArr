import jsonschema
import validators
import yaml
import sys
import os
import logging
import requests
import sqlite3
from colorlog import ColoredFormatter


log_level = logging.DEBUG
log_format = (
    "  %(log_color)s%(levelname)-8s%(reset)s |"
    " %(log_color)s%(message)s%(reset)s"
)

logging.root.setLevel(log_level)
formatter = ColoredFormatter(log_format)

stream = logging.StreamHandler()
stream.setLevel(log_level)
stream.setFormatter(formatter)

LOG = logging.getLogger("pythonConfig")
LOG.setLevel(log_level)
LOG.addHandler(stream)

BOT_TOKEN = None

RADARR_ENABLED = False
RADARR_HOST_URL = None
RADARR_HEADERS = None
RADARR_ROOT_FOLDER_PATH = None
RADARR_QUALITY_PROFILE_ID = None

SONARR_ENABLED = False
SONARR_HOST_URL = None
SONARR_HEADERS = None
SONARR_ROOT_FOLDER_PATH = None
SONARR_QUALITY_PROFILE_ID = None

JELLYFIN_ENABLED = False
JELLYFIN_URL = None
JELLYFIN_HEADERS = None
ACCOUNT_TIME = None
SIMPLE_PASSWORDS = False

schema = {
    "type": "object",
    "properties": {
        "bot_info": {
            "type": "object",
            "properties": {
                "bot_token": {"type": "string"},
            },
            "required": ["bot_token"],
        },
        "radarr": {
            "type": "object",
            "properties": {
                "host_url": {"type": "string"},
                "api_key": {"type": "string"},
                "root_folder_path": {"type": "string"},
                "quality_profile_id": {"type": "integer"},
            },
            "required": [
                "host_url",
                "api_key",
                "root_folder_path",
            ],
        },
        "sonarr": {
            "type": "object",
            "properties": {
                "host_url": {"type": "string"},
                "api_key": {"type": "string"},
                "root_folder_path": {"type": "string"},
                "quality_profile_id": {"type": "integer"},
            },
            "required": [
                "host_url",
                "api_key",
                "root_folder_path",
            ],
        },
        "jellyfin": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "api_key": {"type": "string"},
                "account_time": {"type": "integer"},
            },
            "required": ["url", "api_key", "account_time"],
        },
    },
    "required": ["bot_info", "radarr", "sonarr"],
}


def load_config() -> None:
    """
    Load DB, then load and validate the config file
    If the file does not exist, generate it
    """
    database_setup()
    if os.path.exists("/.dockerenv"):
        file_path = "/config/config.yaml"
    else:
        file_path = "config.yaml"

    try:
        with open(file_path, "r") as f:
            contents = f.read()
            validate_config(contents)

    except FileNotFoundError:
        with open("config.yaml", "w") as f:
            f.write(
                """
bot_info:
    bot_token: YOUR_BOT_TOKEN

radarr:
    host_url: RADARR_URL
    api_key: RADARR_API_KEY
    root_folder_path: RADARR_ROOT_FOLDER_PATH
    quality_profile_id: RADARR_QUALITY_PROFILE_ID

sonarr:
    host_url: SONARR_URL
    api_key: SONARR_API_KEY
    root_folder_path: SONARR_ROOT_FOLDER_PATH
    quality_profile_id: SONARR_QUALITY_PROFILE_ID

jellyfin:
    url: JELLYFIN_URL
    api_key: JELLYFIN_API_KEY
    account_time: ACCOUNT_ACTIVE_TIME
    simple_passwords: SIMPLE_OR_COMPLEX_PASSWORDS
                """
            )

        sys.exit(
            LOG.critical(
                "Config file `config.yaml` has been generated. Input necessary"
                " fields and restart. Refer to README for help!"
            )
        )


def database_setup() -> None:
    """
    Create the database if it does not exist
    """
    db = sqlite3.connect("cordarr.db")
    cursor = db.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS requests (title TEXT, release_year TEXT,"
        " local_id INTEGER, tmdbid INTEGER, tvdbid INTEGER, user_id INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS jellyfin_accounts (user_id INTEGER,"
        " jellyfin_user_id INTEGER, deletion_time DATETIME)"
    )
    db.commit()
    db.close()


def validate_config(contents) -> None:
    """
    Validate the contents of the config file and assign variables

    Args:
        contents (str): The contents of the config file
    """
    global BOT_TOKEN, RADARR_HOST_URL, RADARR_ENABLED, RADARR_HEADERS, RADARR_ROOT_FOLDER_PATH, RADARR_QUALITY_PROFILE_ID, SONARR_ENABLED, SONARR_HOST_URL, SONARR_HEADERS, SONARR_ROOT_FOLDER_PATH, SONARR_QUALITY_PROFILE_ID, JELLYFIN_ENABLED, JELLYFIN_URL, JELLYFIN_HEADERS, ACCOUNT_TIME, SIMPLE_PASSWORDS

    config = yaml.safe_load(contents)

    try:
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        sys.exit(LOG.critical(f"Error in config.yaml: {e.message}"))

    #
    # Begin validating values and assigning variables
    #

    BOT_TOKEN = config["bot_info"]["bot_token"]

    if "radarr" in config:
        if not validators.url(config["radarr"]["host_url"]):
            sys.exit(
                LOG.critical(
                    "Error in config.yaml: Invalid URL for Radarr host"
                )
            )
        else:
            RADARR_HOST_URL = config["radarr"]["host_url"]

        RADARR_HEADERS = {
            "Content-Type": "application/json",
            "X-Api-Key": config["radarr"]["api_key"],
        }
        RADARR_ROOT_FOLDER_PATH = config["radarr"]["root_folder_path"]
        # set radarr quality profile id
        RADARR_QUALITY_PROFILE_ID = validate_profile(
            "radarr", RADARR_HOST_URL, RADARR_HEADERS, config
        )
        RADARR_ENABLED = True

    if "sonarr" in config:
        if not validators.url(config["sonarr"]["host_url"]):
            sys.exit(
                LOG.critical(
                    "Error in config.yaml: Invalid URL for Sonarr host"
                )
            )
        else:
            SONARR_HOST_URL = config["sonarr"]["host_url"]

        SONARR_HEADERS = {
            "Content-Type": "application/json",
            "X-Api-Key": config["sonarr"]["api_key"],
        }
        SONARR_ROOT_FOLDER_PATH = config["sonarr"]["root_folder_path"]
        # set sonarr quality profile id
        SONARR_QUALITY_PROFILE_ID = validate_profile(
            "sonarr", SONARR_HOST_URL, SONARR_HEADERS, config
        )
        SONARR_ENABLED = True

    if "jellyfin" in config:
        if not validators.url(config["jellyfin"]["url"]):
            LOG.critical(
                "Error in config.yaml: Invalid URL for Jellyfin - account"
                " creation disabled"
            )
        else:
            JELLYFIN_URL = config["jellyfin"]["url"]

        JELLYFIN_HEADERS = {
            "Content-Type": "application/json",
            "X-Emby-Token": config["jellyfin"]["api_key"],
        }
        ACCOUNT_TIME = config["jellyfin"]["account_time"]
        SIMPLE_PASSWORDS = config["jellyfin"]
        JELLYFIN_ENABLED = True


def validate_profile(
    service: str, url: str, headers: dict, config: dict
) -> int:
    """
    Validate the quality profile ID for the given service

    Args:
        service (str): The service to validate the profile for
        url (str): The URL of the service
        headers (dict): The headers for the request
        config (dict): The config file

    Returns:
        int: The quality profile ID
    """
    profiles = requests.get(f"{url}/api/v3/qualityProfile", headers=headers)

    if profiles.status_code != 200:
        LOG.critical(
            f"Error in config.yaml: Unable to get {service} quality profiles."
            f" API Key invalid or incorrect {service} URL"
        )

    else:
        profiles = profiles.json()
        # If ID is not given, list options
        if "quality_profile_id" not in config[f"{service}"]:
            LOG.critical(
                "Error in config.yaml: No quality profile ID provided for"
                f" {service}. Look below for a list of your available"
                " profiles:"
            )

            for profile in profiles:
                LOG.info(f"ID: {profile['id']} | Name: {profile['name']}")

        # ID is given, validate
        else:
            quality_profile_id = config[f"{service}"]["quality_profile_id"]
            if quality_profile_id not in [
                profile["id"] for profile in profiles
            ]:
                LOG.critical(
                    f"Error in config.yaml: Invalid {service} quality profile"
                    " ID. Look below for your available profiles:"
                )

                for profile in profiles:
                    LOG.info(f"ID: {profile['id']} | Name: {profile['name']}")
                sys.exit()
            # Everything valid, assign
            else:
                return quality_profile_id
