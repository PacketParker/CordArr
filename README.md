<h1 align="center">
  <br>
  <img src="cordarr.png" width="200" alt="Guava Image"></a>
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

*NOTE: Sonarr support is currently in the works*

# Instructions

CordArr is built on Python and requires you to install all of the dependencies in the `requirements.txt` file. To do this, you can run the pip install command like `pip install -r requirements.txt`

On first run you will likely get a critical warning in your console, don't worry, this is expected. It will automatically create a `config.ini` file for you in the root of the directory with all of the necessary configuration options.

Fill out the configuration options, then re-run the bot, and everything *should* just work. For information on each configuration option, look below.

Field | Description
--- | ---
BOT_TOKEN | The token for your bot. Create a bot at [discord.com/developers](https://discord.com/developers)
RADARR_HOST_URL | URL for your Radarr instance (e.g. http://localhost:7878)
RADARR_API_KEY | API key for Radarr, found in `Settings > General > API Key`
ROOT_FOLDER_PATH | Path for media root folder, found at the bottom of the page in `Settings > Media Management`
QUALITY_PROFILE_ID | ID for the quality profile on Radarr (in order to get a list of your quality profiles and their IDs, set the other fields first, then re-run CordArr, the config.ini file will update with this information)
ENABLE_JELLYFIN_TEMP_ACCOUNT | `true/false` : Whether or not to enable the `/newaccount` command allowing users to create temporary Jellyfin accounts

<br>

If you choose to enable the Jellyfin temp accounts features, these fields will also be required

Field | Description
--- | ---
JELLYFIN_URL | URL for your Jellyfin server (e.g. http://localhost:8096)
JELLYFIN_API_KEY | API key for Jellyfin - can be created in `Dashboard > API Keys`
ACCOUNT_TIME | Amount of time, in hours, that temporary Jellyfin accounts should exist before being deleted

<br>
<br>

If you have any questions, feel free to email at [contact@pkrm.dev](mailto:contact@pkrm.dev). Thank you for checking out Guava, and happy coding.
