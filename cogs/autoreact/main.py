import discord
from discord.ext import commands

from abstracts import AbstractCog
from base import BotBase


class AutoReact(AbstractCog):
    def __init__(self, bot: BotBase) -> None:
        super().__init__(bot)
        
        self.config = self.bot.config["autoreact"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        
async def setup(bot: BotBase) -> None:
    await bot.add_cog(AutoReact(bot))