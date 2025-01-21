import discord
from discord import app_commands
from discord.ext import commands
import requests
import sqlite3

from utils.config import (
    RADARR_HOST_URL,
    RADARR_HEADERS,
    SONARR_HOST_URL,
    SONARR_HEADERS,
)


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def status(self, interaction: discord.Interaction) -> None:
        """Get the status of the movies you have requested"""
        db = sqlite3.connect("data/cordarr.db")
        cursor = db.cursor()
        cursor.execute(
            "SELECT title, release_year, local_id, tmdbid, tvdbid FROM"
            " requests WHERE user_id = ?",
            (interaction.user.id,),
        )
        requested_content = cursor.fetchall()
        db.close()

        # No content requested
        if len(requested_content) == 0:
            embed = discord.Embed(
                title="No Content Requested",
                description=(
                    "If you believe this is in error, the content you have"
                    " requested is likely already downloaded."
                ),
                color=0xD01B86,
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        # Create template embed
        embed = discord.Embed(
            title="Requested Content",
            description=(
                "Below are the movies/shows you have requested that are"
                " currently being downloaded:\n"
            ),
            color=0xD01B86,
        )

        # Unpack the content
        radarr_content_info, sonarr_content_info = self.unpack_content(
            requested_content
        )
        # Get the descriptions and local IDs found in queue
        radarr_desc, radarr_added_ids = self.process_queue(
            radarr_content_info, "radarr"
        )
        sonarr_desc, sonarr_added_ids = self.process_queue(
            sonarr_content_info, "sonarr"
        )

        added_ids = radarr_added_ids + sonarr_added_ids
        # Get the description of content not in the queue
        non_queue_desc = self.get_non_queue_content(
            requested_content, added_ids, interaction.user.id
        )

        embed.description += radarr_desc + sonarr_desc + non_queue_desc

        await interaction.response.send_message(embed=embed, ephemeral=True)

    def unpack_content(self, requested_content: list) -> tuple:
        """
        Given a list of requested content, unpack it into two dictionaries

        Args:
            requested_content (list): A list of requested content

        Returns:
            tuple: A tuple of two dictionaries
        """

        radarr_content_info = {}
        sonarr_content_info = {}

        for content in requested_content:
            title, release_year, local_id, tmdbid, tvdbid = content
            if tmdbid is not None:
                radarr_content_info[local_id] = {
                    "title": title,
                    "release_year": release_year,
                    "tmdbid": tmdbid,
                }
            else:
                sonarr_content_info[local_id] = {
                    "title": title,
                    "release_year": release_year,
                    "tvdbid": tvdbid,
                }

        return radarr_content_info, sonarr_content_info

    def process_queue(self, content_info: dict, service: str) -> str:
        """
        Given a dictionary of requested content and "sonarr"/"radarr", process the queue

        Args:
            content_info (dict): A dictionary of content information
            service (str): The service to check the queue of

        Returns:
            str: The description of the embed
        """

        description = ""
        added_ids = []

        queue = requests.get(
            f"{RADARR_HOST_URL if service == 'radarr' else SONARR_HOST_URL}/api/v3/queue",
            headers=RADARR_HEADERS if service == "radarr" else SONARR_HEADERS,
        ).json()

        for download in queue["records"]:
            id_str = "movieId" if service == "radarr" else "seriesId"
            # If the content was requested by the user
            if (
                download[id_str] in content_info.keys()
                and download[id_str] not in added_ids
            ):
                # Append local ID
                added_ids.append(download[id_str])
                # Add the download to the embed
                try:
                    time_left = self.process_time(download["timeleft"])
                except KeyError:
                    time_left = "Unknown"
                description += (
                    f"\n**{content_info[download[id_str]]['title']} ({content_info[download[id_str]]['release_year']})**"
                    f" - Time Left: `{time_left}`"
                )

        return description, added_ids

    def get_non_queue_content(
        self, requested_content: list, added_ids: list, user_id: int
    ) -> str:
        """
        Given a list of requested content and a list of added IDs, return a description of content not in the queue

        Args:
            requested_content (list): A list of requested content
            added_ids (list): A list of IDs that are in the queue
            user_id (int): The ID of the user

        Returns:
            str: A description of content not in the queue
        """

        description = ""
        # For evry piece of content not in the queue, check if it has a file
        for content in requested_content:
            title, release_year, local_id, tmdbid, _ = content
            # If not in queue
            if local_id not in added_ids:
                # Pull the movie data from the service
                if tmdbid is not None:
                    data = requests.get(
                        f"{RADARR_HOST_URL}/api/v3/movie/{local_id}",
                        headers=RADARR_HEADERS,
                    ).json()
                else:
                    data = requests.get(
                        f"{SONARR_HOST_URL}/api/v3/series/{local_id}",
                        headers=SONARR_HEADERS,
                    ).json()

                # If the movie has a file, then it has finished downloading
                if data.get("hasFile", True):
                    # Remove from database
                    db = sqlite3.connect("data/cordarr.db")
                    cursor = db.cursor()
                    cursor.execute(
                        "DELETE FROM requests WHERE user_id = ? AND"
                        " local_id = ?",
                        (user_id, local_id),
                    )
                    db.commit()
                    db.close()
                # If series and only a portion of episodes have been downloaded
                if data.get("statistics").get("percentOfEpisodes"):
                    description += (
                        f"\n**{title} ({release_year})** - Status: `NOT"
                        " FOUND"
                        f" ({int(data['statistics']['percentOfEpisodes'])}%"
                        " of eps.)`"
                    )
                # All other scenarios, download not found
                else:
                    description += (
                        f"\n**{title} ({release_year})** - Status: `NOT FOUND`"
                    )

        return description

    def process_time(self, time) -> str:
        """
        Given a time string, process it into a human readable format

        Args:
            time (str): A string representing time

        Returns:
            str: A human readable time
        """
        # Split the input by either ':' or spaces
        parts = time.replace(" ", ":").replace(".", ":").split(":")

        # Handle different input lengths
        if len(parts) == 2:  # Format: MM:SS
            minutes, seconds = map(int, parts)
            return f"{minutes} min. {seconds} sec."

        elif len(parts) == 3:  # Format: HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            if hours == 0:
                return f"{minutes} min. {seconds} sec."
            return f"{hours} hr. {minutes} min."

        elif len(parts) == 4:  # Format: D:HH:MM:SS
            days, hours, minutes, seconds = map(int, parts)
            if days == 0:
                return f"{hours} hr. {minutes} min."
            return f"{days} days {hours} hr."

        else:
            return "Unknown"


async def setup(bot):
    await bot.add_cog(Status(bot))
