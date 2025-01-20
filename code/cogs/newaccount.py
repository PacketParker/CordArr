import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

from utils.jellyfin_create import create_jellyfin_account
from utils.config import (
    JELLYFIN_URL,
    JELLYFIN_ENABLED,
    ACCOUNT_TIME,
)


class NewAccount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.check(lambda inter: JELLYFIN_ENABLED)
    async def newaccount(self, interaction: discord.Interaction) -> None:
        """Create a new temporary Jellyfin account"""
        # Make sure the user doesn't already have an account
        db = sqlite3.connect("cordarr.db")
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM jellyfin_accounts WHERE user_id = ?",
            (interaction.user.id,),
        )
        account = cursor.fetchone()
        db.close()
        # Account already allocated
        if account:
            embed = discord.Embed(
                title="Account Already Exists",
                description=(
                    "Look at your previous DMs with me to find your account"
                    " information. You will be permitted to create a new"
                    " account after your current one expires."
                ),
                color=0xD01B86,
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        # Create a new Jellyfin account for the user
        response = create_jellyfin_account(interaction.user.id)
        if response:
            embed = discord.Embed(
                title="Account Created",
                description=(
                    "Your account has been successfully created. Check your"
                    " DMs for your account information."
                ),
                color=0xD01B86,
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

            # Send the user their account information
            embed = discord.Embed(
                title="Jellyfin Account Information",
                description=(
                    # fmt: off
                    "Here is your temporary account information.\n\n"
                    f"**Server URL:** `{JELLYFIN_URL}`\n"
                    f"**Username:** `{response[0]}`\n"
                    f"**Password:** `{response[1]}`\n\n"
                    "Your account will be automatically deleted in"
                    f" {ACCOUNT_TIME} hours."
                    # fmt: on
                ),
                color=0xD01B86,
            )
            await interaction.user.send(embed=embed)
        # If account not created for some reason
        else:
            embed = discord.Embed(
                title="Unknown Error Occured",
                description=(
                    "Error creating Jellyfin account. Please try again. If the"
                    " error persists, contact an administrator."
                ),
                color=0xD01B86,
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(NewAccount(bot))
