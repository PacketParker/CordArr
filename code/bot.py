import discord
from discord.ext import commands
from discord.ext import tasks
import datetime
import sqlite3
import os

from validate_config import create_config
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
    # Delete all of the temporary Jellyfin accounts that have passed
    # their expiration time
    db = sqlite3.connect("cordarr.db")
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM jellyfin_accounts WHERE deletion_time < ?",
        (datetime.datetime.now(),),
    )
    db.commit()
    db.close()


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
