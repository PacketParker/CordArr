import requests


def add_content(
    content_info: dict,
    service: str,
    host: str,
    headers: str,
    folder_path: str,
    profile_id: str,
):
    """
    Add content to Sonarr or Radarr

    Args:
        content_info (dict): The content information
        service (str): The service to add the content to
        host (str): The host URL
        headers (str): The headers for the request
        folder_path (str): The folder path to download the content to
        profile_id (str): The profile ID to download the content in

    Returns:
        str: The ID of the content or False
    """
    # Get the content data based on ID
    data = requests.get(
        url=(
            f"{host}/api/v3/movie/lookup/tmdb?tmdbId={content_info['contentId']}"
            if service == "radarr"
            else f"{host}/api/v3/series/lookup?term=tvdb:{content_info['contentId']}"
        ),
        headers=headers,
    ).json()[0]

    data["monitored"] = True
    data["qualityProfileId"] = profile_id
    data["rootFolderPath"] = folder_path
    # Search for the content on add
    data["addOptions"] = {
        (
            "searchForMovie"
            if service == "radarr"
            else "searchForMissingEpisodes"
        ): True
    }
    # Send the request to add the content
    response = requests.post(
        f"{host}/api/v3/{'movie' if service == 'radarr' else 'series'}",
        headers=headers,
        json=data,
    )

    if response.status_code == 201:
        return response.json()["id"]
    else:
        return False
