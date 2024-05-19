import discord
from discord import app_commands
from discord.ext import commands
import requests
import sqlite3
import datetime
import humanize

from global_variables import RADARR_HOST_URL, RADARR_HEADERS


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def status(self, interaction: discord.Interaction):
        "Get the status of the movies you have requested"
        # Get all the movie_ids that were requested by the user
        db = sqlite3.connect("cordarr.db")
        cursor = db.cursor()
        cursor.execute(
            "SELECT movie_id, movie_title FROM movies WHERE user_id = ?",
            (interaction.user.id,),
        )
        requested_movies = cursor.fetchall()

        users_movies = {}  # Dictionary to store the movies that the user has requested
        for movie_id, movie_title in requested_movies:
            users_movies[movie_id] = movie_title
        # If theres no movies, return a message saying so
        if not users_movies:
            embed = discord.Embed(
                title="No Movies Requested",
                description="You have no movies being downloaded at the moment. If you previously added a movie, it is likely that it has finished downloading. If you believe this is an error, please contact an administrator.",
                color=0xD01B86
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        # Otherwise, create the default embed to display the movies being downloaded
        embed = discord.Embed(
            title="Movies Requested",
            description="Here are the movies you have requested that are currently being downloaded:\n",
            color=0xD01B86
        )

        # Now, we get the download status of all movies from the Radarr queue
        response = requests.get(
            f"{RADARR_HOST_URL}/api/v3/queue/", headers=RADARR_HEADERS
        ).json()

        count = 0
        added_movie_ids = []
        for movie in response["records"]:
            movie_id = movie["movieId"]
            # If the movie is user requested and is being downloaded
            if movie_id in users_movies.keys():
                count += 1
                added_movie_ids.append(movie_id)
                if movie["status"] == "downloading":
                    # Humanize the download time left, or result to 'Unknown
                    try:
                        time_left = humanize.precisedelta(
                            datetime.datetime.strptime(movie["timeleft"], "%H:%M:%S")
                            - datetime.datetime.strptime("00:00:00", "%H:%M:%S"),
                            minimum_unit="seconds",
                        )
                    except ValueError:
                        # Sometimes movies will download extremely show and therefore might
                        # show 'days' in the time left, so strptime appropriately
                        time_left = humanize.precisedelta(
                            datetime.datetime.strptime(movie["timeleft"], "%d.%H:%M:%S")
                            - datetime.datetime.strptime("00:00:00", "%H:%M:%S"),
                            minimum_unit="seconds",
                        )
                    except KeyError or ValueError:
                        time_left = "Unknown"

                    # Add all the information
                    embed.description += f"\n{count}. **{users_movies[movie_id]}** - Time Left: ` {time_left} `"
                else:
                    embed.description += f"\n{count}. **{users_movies[movie_id]}** - Status: `{str(movie['status']).upper()}`"

        # If a movie wasn't found in the Radarr queue, then it has either finished downloading
        # or the movie was never found for download
        if len(added_movie_ids) != len(users_movies.keys()):
            # Grab all of the "missing" movies to see if a movie is missing or finished downloading
            response = requests.get(
                f"{RADARR_HOST_URL}/api/v3/wanted/missing", headers=RADARR_HEADERS
            ).json()
            for movie in response["records"]:
                movie_id = movie["id"]
                if movie_id in users_movies.keys() and movie_id not in added_movie_ids:
                    count += 1
                    added_movie_ids.append(movie_id)
                    embed.description += f"\n{count}. **{users_movies[movie_id]}** - Status: ` NOT FOUND `"
        # If there are still movies that haven't been added to the embed, then they
        # have finished downloading and can be removed from the database
        for movie_id in users_movies.keys():
            if movie_id not in added_movie_ids:
                cursor.execute(
                    "DELETE FROM movies WHERE user_id = ? AND movie_id = ?",
                    (interaction.user.id, movie_id),
                )
        db.commit()
        db.close()

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Status(bot))
