import requests
import sqlite3
import discord

from global_variables import (
    RADARR_HOST_URL,
    RADARR_HEADERS,
    ROOT_FOLDER_PATH,
    QUALITY_PROFILE_ID,
)

"""
Add a specific movie to the Radarr library
"""


def get_movies(name: str):
    # Remove leading/trailing whitespace and replace spaces with URL encoding
    name = name.strip().replace(" ", "%20")

    # Send a request to the Radarr API to search for the movie
    response = requests.get(
        f"{RADARR_HOST_URL}/api/v3/movie/lookup?term={name}", headers=RADARR_HEADERS
    ).json()

    if len(response) == 0:
        return "NO RESULTS"
    # If the movie has alreadt been added, then the added date will be
    # something other than 0001-01-01T05:51:00Z
    if response[0]["added"] != "0001-01-01T05:51:00Z":
        return "ALREADY ADDED"

    movie_data = []
    for i in range(min(5, len(response))):
        movie_data.append(
            {
                "title": response[i]["title"],
                "year": response[i]["year"],
                "tmdbId": response[i]["tmdbId"],
                "description": response[i]["overview"],
            }
        )

        try:
            try:
                movie_data[i]["remotePoster"] = response[i]["images"][0]["remoteUrl"]
            except IndexError:
                movie_data[i]["remotePoster"] = response[i]["images"][1]["remoteUrl"]
        except IndexError:
            movie_data[i]["remotePoster"] = None

    return movie_data


"""
Send a request to the Radarr API to add the movie
"""


def add_movie(tmdb_id: int):
    # Get the necessary data for the movie
    data = requests.get(
        f"{RADARR_HOST_URL}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}",
        headers=RADARR_HEADERS,
    ).json()

    movie_title = data["title"]
    # Change the qualityProfileId, monitored, and rootFolderPath values
    data["qualityProfileId"] = QUALITY_PROFILE_ID
    data["monitored"] = True
    data["rootFolderPath"] = ROOT_FOLDER_PATH
    # Send the request to add the movie
    response = requests.post(
        f"{RADARR_HOST_URL}/api/v3/movie", headers=RADARR_HEADERS, json=data
    ).json()
    movie_id = response["id"]

    # Return the movie_title, movie_id
    return movie_title, movie_id


class AddMovieView(discord.ui.View):
    def __init__(self, movie_data: list, *, timeout=180.0):
        super().__init__(timeout=timeout)
        self.add_item(AddMovieDropdown(movie_data))


class AddMovieDropdown(discord.ui.Select):
    def __init__(self, movie_data: list, *, timeout=180.0):
        self.movie_data = movie_data
        # Create the options list to show the movie title, year, and tmdbId
        options = []
        for i in range(len(movie_data)):
            options.append(
                discord.SelectOption(
                    label=f"{movie_data[i]['title']} ({movie_data[i]['year']})",
                    description=f"TMDB ID: {movie_data[i]['tmdbId']}",
                    value=i,
                )
            )

        super().__init__(
            placeholder="Select from the dropdown",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])

        embed = discord.Embed(
            title="Is this the movie you want to add?",
            description=f"**{self.movie_data[index]['title']}**\n\n{self.movie_data[index]['description']}",
            color=0xD01B86,
        )
        embed.set_image(url=self.movie_data[index]["remotePoster"])
        view = RequestButtonView(self.movie_data[index]["tmdbId"])
        await interaction.response.edit_message(embed=embed, view=view)


class RequestButtonView(discord.ui.View):
    def __init__(self, tmdb_id: int, *, timeout=180.0):
        super().__init__(timeout=timeout)
        self.tmdb_id = tmdb_id

    @discord.ui.button(label="Request", style=discord.ButtonStyle.success)
    async def request_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # Add the movie to the Radarr library
        movie_title, movie_id = add_movie(self.tmdb_id)

        # Alert the user that the movie has been added
        embed = discord.Embed(
            title="Movie Requested",
            description=f"**{movie_title}** has been requested and will be added to the Radarr library. You can check the download status of your requested movies by running the `/status` command. Please wait ~5 minutes for Radarr to find a download for the movie.",
            color=0xD01B86,
        )
        await interaction.response.edit_message(embed=embed, view=None)
        # Force Radarr to search for the movie
        requests.post(
            f"{RADARR_HOST_URL}/api/v3/command",
            headers=RADARR_HEADERS,
            json={"name": "MoviesSearch", "movieIds": [movie_id]},
        )

        # Keep track of the movie for the `/status` command
        db = sqlite3.connect("cordarr.db")
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO movies VALUES (?, ?, ?)",
            (interaction.user.id, movie_id, movie_title),
        )
        db.commit()
        db.close()

    @discord.ui.button(label="Don't Request", style=discord.ButtonStyle.danger)
    async def dont_request_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="Request Cancelled",
            description="Request has been cancelled. If you would like to request a different movie, run the `/request movie` command again.",
            color=0xD01B86,
        )
        await interaction.response.edit_message(embed=embed, view=None)
