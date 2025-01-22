import discord
from discord.ext import commands, tasks
import os

from utils.database import Base, engine
import utils.config as config


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="#",
            intents=discord.Intents.default(),
        )

    async def setup_hook(self):
        delete_accounts_task.start()
        for ext in os.listdir("./code/cogs"):
            if ext.endswith(".py"):
                await self.load_extension(f"cogs.{ext[:-3]}")


bot = MyBot()
bot.remove_command("help")


@bot.event
async def on_ready():
    config.LOG.info(f"{bot.user} has connected to Discord.")


@tasks.loop(minutes=1)
async def delete_accounts_task():
    from utils.jellyfin_delete import delete_accounts

    Base.metadata.create_all(bind=engine)
    delete_accounts()


if __name__ == "__main__":
    config.load_config()
    bot.run(config.BOT_TOKEN)
