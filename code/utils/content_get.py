import requests


def get_content(
    query: str,
    service: str,
    host: str,
    headers: str,
):
    """
    Fetch the top 5 results from the service given a query

    Args:
        query (str): The query to search for
        service (str): The service to search in
        host (str): The host URL
        headers (str): The headers for the request

    Returns:
        list: A list containing content_info dict
        str: NO RESULTS
        str: ALREADY ADDED
    """
    query = query.strip().replace(" ", "%20")
    # Search for matching content
    results = requests.get(
        f"{host}/api/v3/{'movie' if service == 'radarr' else 'series'}/lookup?term={query}",
        headers=headers,
    ).json()

    if len(results) == 0:
        return "NO RESULTS"
    # If already added to library
    if results[0]["added"] != "0001-01-01T05:51:00Z":
        return "ALREADY ADDED"

    # Add info for top results
    content_info = []
    for i in range(min(5, len(results))):
        content_info.append(
            {
                "title": results[i]["title"],
                "year": results[i]["year"],
                "contentId": results[i][
                    f"{'tmdbId' if service == 'radarr' else 'tvdbId'}"
                ],
            }
        )

        # Add overview field, set None if not available
        try:
            content_info[i]["description"] = results[i]["overview"]
        except KeyError:
            content_info[i]["description"] = "No description available"

        # Add remotePoster field, set None if not available
        try:
            content_info[i]["remotePoster"] = results[i]["images"][0][
                "remoteUrl"
            ]
        except IndexError:
            content_info[i]["remotePoster"] = None

    return content_info
