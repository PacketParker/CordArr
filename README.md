<h1 align="center">
  <br>
  <img src="cordarr.png" width="200" alt="CordArr Logo"></a>
  <br>
  CordArr<br>
</h1>

<h3 align="center">
    Control your Radarr/Sonarr library and create Jellyfin accounts in Discord
</h3>

<p align="center">
  <a href="https://github.com/Rapptz/discord.py/">
     <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
  </a>
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg">
  </a>
</p>

# Overview

CordArr is a self-hosted Discord bot that allows you to add new movies or shows to your Radarr/Sonarr libraries, and allow users to create temporary Jellyfin accounts on your server.

# Instructions

CordArr is built on Python and requires you to install all of the dependencies in the `requirements.txt` file. To do this, you can run the pip install command like `pip install -r requirements.txt`

You must then fill out the `config.yaml` file with the necessary information. If the file does not exist already, run the bot once to generate the file.

# Configuration
## BOT_INFO
Field | Description
--- | ---
BOT_TOKEN | The token for your bot. Create a bot at [discord.com/developers](https://discord.com/developers)

## RADARR / SONARR | OPTIONAL
Field | Description
--- | ---
HOST_URL | URL for your Radarr/Sonarr instance (e.g. http://localhost:7878)
API_KEY | API key for Radarr/Sonarr, found in `Settings > General > API Key`
ROOT_FOLDER_PATH | Folder path found at the bottom of the page in `Settings > Media Management`
QUALITY_PROFILE_ID | ID for the quality profile to download content in. Run the bot once to get a list of profiles and their IDs

## JELLYFIN | OPTIONAL
Field | Description
--- | ---
URL | URL for your Jellyfin server (e.g. http://localhost:8096)
API_KEY | API key for Jellyfin - can be created in `Dashboard > API Keys`
ACCOUNT_TIME | Amount of time, in hours, accounts should exist before being deleted
SIMPLE_PASSWORDS | `true/false` : Whether or not to have simple dictionary word passwords for temporary accounts