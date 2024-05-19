import configparser
import sqlite3
import requests
from global_variables import LOG, YES_VALUES, NO_VALUES

"""
Validate all of the options passed into the config.ini file
"""


def validate_config(file_contents):
    config = configparser.ConfigParser()
    config.read_string(file_contents)

    errors = 0

    try:
        # Validate BOT_TOKEN
        if not config["REQUIRED"]["BOT_TOKEN"]:
            LOG.error("BOT_TOKEN has not been set.")
            errors += 1

        # Validate RADARR_HOST_URL
        if not config["REQUIRED"]["RADARR_HOST_URL"]:
            LOG.error("RADARR_HOST_URL has not been set.")
            errors += 1

        # Validate RADARR_API_KEY
        if not config["REQUIRED"]["RADARR_API_KEY"]:
            LOG.error("RADARR_API_KEY has not been set.")
            errors += 1

        radarr_headers = {
            "Content-Type": "application/json",
            "X-Api-Key": config["REQUIRED"]["RADARR_API_KEY"],
        }

        # Make sure connection to Radarr API can be established
        try:
            requests.get(config["REQUIRED"]["RADARR_HOST_URL"], headers=radarr_headers)
        except requests.exceptions.ConnectionError:
            LOG.error("Could not connect to Radarr API. Please check your RADARR_HOST_URL and RADARR_API_KEY")
            errors += 1

        # Validate ROOT_FOLDER_PATH
        if not config["REQUIRED"]["ROOT_FOLDER_PATH"]:
            LOG.error("ROOT_FOLDER_PATH has not been set.")
            errors += 1

        # Validate QUALITY_PROFILE_ID
        data = requests.get(
            f'{config["REQUIRED"]["RADARR_HOST_URL"]}/api/v3/qualityprofile',
            headers=radarr_headers,
        ).json()
        all_ids = []
        for entry in data:
            all_ids.append(str(entry["id"]))

        if (
            not config["REQUIRED"]["QUALITY_PROFILE_ID"]
            or config["REQUIRED"]["QUALITY_PROFILE_ID"] not in all_ids
        ):
            config["AVAILABLE_QUALITY_IDS"] = {}
            for entry in data:
                config["AVAILABLE_QUALITY_IDS"][str(entry["id"])] = entry["name"]

            LOG.error("Empty or invalid QUALITY_PROFILE_ID passed. Pass one of the valid IDs which are now listed within the config.ini file.")
            errors += 1

        # Validate ENABLE_JELLYFIN_TEMP_ACCOUNTS
        if not config["REQUIRED"]["ENABLE_JELLYFIN_TEMP_ACCOUNTS"]:
            LOG.error("ENABLE_JELLYFIN_TEMP_ACCOUNTS has not been set.")
            errors += 1

        else:
            # Validate the value of ENABLE_JELLYFIN_TEMP_ACCOUNTS
            if (config["REQUIRED"]["ENABLE_JELLYFIN_TEMP_ACCOUNTS"].lower() not in YES_VALUES + NO_VALUES):
                LOG.error("Invalid value passed to ENABLE_JELLYFIN_TEMP_ACCOUNTS. Pass a true/false value.")
                errors += 1

            if (config["REQUIRED"]["ENABLE_JELLYFIN_TEMP_ACCOUNTS"].lower() in YES_VALUES):
                # Validate JELLYFIN_URL
                if not config["JELLYFIN_ACCOUNTS"]["JELLYFIN_URL"]:
                    LOG.error("Empty URL passed to JELLYFIN_URL. Pass a valid URL (e.g. http://localhost:8096)")
                    errors += 1
                # Validate JELLYFIN_API_KEY
                if not config["JELLYFIN_ACCOUNTS"]["JELLYFIN_API_KEY"]:
                    LOG.error("Empty JELLYFIN_API_KEY passed. Create a Jellyfin API key in your Jellyfin dashboard and pass it here.")
                    errors += 1
                # Validate ACCOUNT_TIME
                if not config["JELLYFIN_ACCOUNTS"]["ACCOUNT_TIME"]:
                    LOG.error("Empty ACCOUNT_TIME passed. Pass a valid time in the format of HH:MM:SS (e.g. 00:30:00)")
                    errors += 1
                try:
                    time = int(config["JELLYFIN_ACCOUNTS"]["ACCOUNT_TIME"])
                except ValueError:
                    LOG.error("Invalid value passed to ACCOUNT_TIME. Pass a valid integer value (e.g. 24)")
                    errors += 1

                # Make sure connection to Jellyfin API can be established
                jellyfin_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"MediaBrowser Client=\"other\", device=\"CordArr\", DeviceId=\"cordarr-device-id\", Version=\"0.0.0\", Token=\"{config['JELLYFIN_ACCOUNTS']['JELLYFIN_API_KEY']}\"",
                }

                response = requests.get(
                    f"{config['JELLYFIN_ACCOUNTS']['JELLYFIN_URL']}/Users",
                    headers=jellyfin_headers,
                )
                if response.status_code != 200:
                    LOG.error("Could not connect to Jellyfin API. Please check your JELLYFIN_URL and JELLYFIN_API_KEY")
                    errors += 1

        if errors > 0:
            LOG.info(f"Found {errors} error(s) in the configuration file. Please fix them before restarting the application.")
            exit()

    except KeyError:
        LOG.critical("You are missing at least one of the configuration options in your config.ini file. In order to regenerate all options, delete the config.ini file and restart the application.")
        exit()


"""
This method is called before starting the application - to make and validate the configuration
"""


def create_config():
    # While here, we can begin by making the database
    db = sqlite3.connect("cordarr.db")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (user_id, movie_id, movie_title)")
    cursor.execute("CREATE TABLE IF NOT EXISTS jellyfin_accounts (user_id, jellyfin_user_id, deletion_time, PRIMARY KEY (user_id))")
    db.commit()
    db.close()

    # Attempt to open and validate the configuration file
    try:
        with open("config.ini", "r") as config:
            file_contents = config.read()
            validate_config(file_contents)

    except FileNotFoundError:
        try:
            with open("/data/config.ini", "r") as config:
                file_contents = config.read()
                validate_config(file_contents)

        except FileNotFoundError:
            # Create the config.ini file
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
