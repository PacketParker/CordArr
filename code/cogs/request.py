import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal

from utils.content_get import get_content
from utils.content_view import AddContentView
from utils.config import (
    RADARR_HOST_URL,
    RADARR_HEADERS,
    RADARR_ROOT_FOLDER_PATH,
    RADARR_QUALITY_PROFILE_ID,
    SONARR_HOST_URL,
    SONARR_HEADERS,
    SONARR_ROOT_FOLDER_PATH,
    SONARR_QUALITY_PROFILE_ID,
)


class Request(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(form="Are you requesting a Movie or Show?")
    @app_commands.describe(name="Name of the content")
    async def request(
        self,
        interaction: discord.Interaction,
        form: Literal["Movie", "Show"],
        name: str,
    ) -> None:
        """Request a movie or tv show to be added to the library"""
        # Get matching content from relevant service
        if form == "Movie":
            content_data = get_content(
                name, "radarr", RADARR_HOST_URL, RADARR_HEADERS
            )
        else:
            content_data = get_content(
                name, "sonarr", SONARR_HOST_URL, SONARR_HEADERS
            )

        if content_data == "NO RESULTS":
            embed = discord.Embed(
                title="No Results",
                description=(
                    # fmt: off
                    "No results found, please try again. Here are some tips:\n\n"
                    "1. Double check spelling\n"
                    "2. Add release year to the query\n"
                    "3. Double check the \"Movie\" or \"Show\" option"
                    # fmt: on
                ),
                color=0xD01B86,
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        if content_data == "ALREADY ADDED":
            embed = discord.Embed(
                title="Already Added",
                description=(
                    f"**{name}** is already added to the"
                    f" {'radarr' if form == 'Movie' else 'sonarr'} library. It"
                    " may be downloading, stalled, or not found. Check the"
                    " status of the content you have requested with"
                    " `/status`."
                ),
                color=0xD01B86,
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        embed = discord.Embed(
            title="Results Found",
            description=(
                f"Please select from the top {len(content_data)} results from"
                f" {'radarr' if form == 'Movie' else 'sonarr'} in the"
                " dropdown below."
            ),
            color=0xD01B86,
        )
        # Create view with the content data and relevant service info
        if form == "Movie":
            view = AddContentView(
                content_data,
                "radarr",
                RADARR_HOST_URL,
                RADARR_HEADERS,
                RADARR_ROOT_FOLDER_PATH,
                RADARR_QUALITY_PROFILE_ID,
            )
        else:
            view = AddContentView(
                content_data,
                "sonarr",
                SONARR_HOST_URL,
                SONARR_HEADERS,
                SONARR_ROOT_FOLDER_PATH,
                SONARR_QUALITY_PROFILE_ID,
            )

        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Request(bot))
