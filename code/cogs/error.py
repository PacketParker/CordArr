import discord
from discord.ext import commands
from discord import app_commands


class slash_handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = self.on_error

    async def on_error(self, interaction: discord.Interaction, error):
        if (
            isinstance(error, app_commands.CheckFailure)
            and interaction.command.name == "newaccount"
        ):
            embed = discord.Embed(
                title="Jellyfin Account Creation Disabled",
                description=f"The owner of {self.bot.user.mention} has disabled the ability to create temporary Jellyfin accounts. Contact an administrator for more information.",
                color=0xD01B86
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(slash_handlers(bot))
