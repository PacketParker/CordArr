import discord
from discord.ext import commands
from discord.ext import tasks
import os

import utils.config as config
from utils.jellyfin_delete import delete_accounts


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="#",
            intents=discord.Intents.default(),
        )

    async def setup_hook(self):
        delete_old_temp_accounts.start()
        for ext in os.listdir("./code/cogs"):
            if ext.endswith(".py"):
                await self.load_extension(f"cogs.{ext[:-3]}")


bot = MyBot()
bot.remove_command("help")


@bot.event
async def on_ready():
    config.LOG.info(f"{bot.user} has connected to Discord.")


@tasks.loop(seconds=60)
async def delete_old_temp_accounts():
    delete_accounts()


if __name__ == "__main__":
    config.load_config()
    bot.run(config.BOT_TOKEN)
