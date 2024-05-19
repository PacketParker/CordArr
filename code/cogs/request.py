import discord
from discord import app_commands
from discord.ext import commands

from func.radarr import get_movies, AddMovieView


class Request(commands.GroupCog, name="request"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="movie")
    @app_commands.describe(name="Name of the movie to add")
    async def request_movie(self, interaction: discord.Interaction, name: str):
        "Request a movie to be added to the Radarr library"
        get_movies_response = get_movies(name)
        if get_movies_response == "NO RESULTS":
            embed = discord.Embed(
                title="No Results",
                description="No results were found for the given movie name. If you are unable to find the movie, contact an administrator to have it added manually.",
                color=0xD01B86
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if get_movies_response == "ALREADY ADDED":
            embed = discord.Embed(
                title="Already Added",
                description="The movie you are trying to add has already been added to the Radarr library.\n\nYou can check the download status of your requests movies by running the `/status` command.",
                color=0xD01B86
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        movies, tmdb_ids = get_movies_response

        embed = discord.Embed(
            title="Results Found",
            description="Please select the movie you would like to add from the dropdown below.",
            color=0xD01B86
        )
        view = AddMovieView(movies, tmdb_ids)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="show")
    @app_commands.describe(name="Name of the show/series to add")
    async def request_show(self, interaction: discord.Interaction, name: str):
        "Request a show/series to be added to the Sonarr library"
        embed = discord.Embed(
            title="Coming Soon",
            description="This feature is not yet implemented. Check back later.",
            color=0xD01B86
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Request(bot))
