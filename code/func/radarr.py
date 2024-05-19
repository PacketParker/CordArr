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

    # Add the top 5 movies and their years to a list of dictionaries and their respective tmdbIds
    movies = [
        {"title": response[i]["title"], "year": response[i]["year"]}
        for i in range(min(5, len(response)))
    ]
    tmdb_ids = {}
    for i in range(min(5, len(response))):
        tmdb_ids[response[i]["tmdbId"]] = {"description": response[i]["overview"]}
        # Try to choose from one of the usual 2 poster images available,
        # if not, then just set the "poster" to None
        try:
            try:
                tmdb_ids[response[i]["tmdbId"]]["remotePoster"] = response[i]["images"][0]["remoteUrl"]
            except IndexError:
                tmdb_ids[response[i]["tmdbId"]]["remotePoster"] = response[i]["images"][1]["remoteUrl"]
        except IndexError:
            tmdb_ids[response[i]["tmdbId"]]["remotePoster"] = None

    return movies, tmdb_ids


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
    def __init__(self, movies: list, tmdb_ids: dict, *, timeout=180.0):
        super().__init__(timeout=timeout)
        self.add_item(AddMovieDropdown(movies, tmdb_ids))


class AddMovieDropdown(discord.ui.Select):
    def __init__(self, movies: list, tmdb_ids: dict, *, timeout=180.0):
        self.movies = movies
        self.tmdb_ids = tmdb_ids
        super().__init__(
            placeholder="Select from the dropdown",
            options=[
                discord.SelectOption(label=f"{movie['title']} ({movie['year']})")
                for movie in movies
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        # Convert the options to a list of strings and get the index of the selected option
        string_options = [option.label for option in self.options]
        index = string_options.index(interaction.data["values"][0])
        # Convert the tmdbIds dictionary to a list and get the tmdbId of the selected movie
        tmdb_id_list = list(self.tmdb_ids.keys())
        tmdb_id = tmdb_id_list[index]
        tmdbFull = self.tmdb_ids[tmdb_id]

        embed = discord.Embed(
            title="Is this the movie you want to add?",
            description=f"**{self.movies[index]['title']}**\n\n{tmdbFull['description']}",
            color=0xD01B86
        )
        embed.set_image(url=tmdbFull["remotePoster"])
        view = RequestButtonView(tmdb_id)
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
            color=0xD01B86
        )
        await interaction.response.edit_message(embed=embed, view=None)
        # # Add the movie to the Radarr library
        # requests.post(
        #     f"{RADARR_HOST_URL}/api/v3/command",
        #     headers=RADARR_HEADERS,
        #     json={"name": "MoviesSearch", "movieIds": movie_id},
        # )

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
            color=0xD01B86
        )
        await interaction.response.edit_message(embed=embed, view=None)
