import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

from func.jellyfin import create_jellyfin_account
from global_variables import JELLYFIN_URL, ENABLE_JELLYFIN_TEMP_ACCOUNTS, ACCOUNT_TIME


class NewAccount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.check(lambda inter: ENABLE_JELLYFIN_TEMP_ACCOUNTS)
    async def newaccount(self, interaction: discord.Interaction):
        "Create a new temporary Jellyfin account"
        # Make sure the user doesn't already have an account
        db = sqlite3.connect("cordarr.db")
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM jellyfin_accounts WHERE user_id = ?", (interaction.user.id,)
        )
        if cursor.fetchone():
            embed = discord.Embed(
                title="Account Already Exists",
                description="Look at your previous DMs with me to find your account information. You will be permitted to create a new account after your current one expires.",
                color=0xD01B86
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Create a new Jellyfin account for the user
        response = create_jellyfin_account(interaction.user.id)
        if response:
            embed = discord.Embed(
                title="Account Created",
                description="Your account has been successfully created. Check your DMs for your account information.",
                color=0xD01B86
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Send the user their account information
            embed = discord.Embed(
                title="Jellyfin Account Information",
                description=f"Here is your temporary account information. You will need this to access the Jellyfin server.\n\n**Server URL:** `{JELLYFIN_URL}`\n**Username:** `{response[0]}`\n**Password:** `{response[1]}`\n\nYour account will be automatically deleted in {ACCOUNT_TIME} hours.",
                color=0xD01B86
            )
            await interaction.user.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Unknown Error Occured",
                description="Error creating Jellyfin account. Please try again. If the error persists, contact an administrator.",
                color=0xD01B86
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(NewAccount(bot))
