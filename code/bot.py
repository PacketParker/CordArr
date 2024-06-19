import discord
from discord.ext import commands
from discord.ext import tasks
import datetime
import sqlite3
import os

from validate_config import create_config
from func.jellyfin import delete_jellyfin_account
from global_variables import LOG, BOT_TOKEN


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="#",
            intents=discord.Intents.default(),
        )

    async def setup_hook(self):
        create_config()
        delete_old_temp_accounts.start()
        for ext in os.listdir("./code/cogs"):
            if ext.endswith(".py"):
                await self.load_extension(f"cogs.{ext[:-3]}")


bot = MyBot()
bot.remove_command("help")


@bot.event
async def on_ready():
    LOG.info(f"{bot.user} has connected to Discord.")


@tasks.loop(seconds=60)
async def delete_old_temp_accounts():
    # Get all jellyfin user IDs that have passed their deletion time
    db = sqlite3.connect("cordarr.db")
    cursor = db.cursor()
    cursor.execute("SELECT jellyfin_user_id FROM jellyfin_accounts WHERE deletion_time < ?", (datetime.datetime.now(),))
    jellyfin_user_ids = cursor.fetchall()

    # Delete the Jellyfin accounts
    for jellyfin_user_id in jellyfin_user_ids:
        delete_jellyfin_account(jellyfin_user_id[0])


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
