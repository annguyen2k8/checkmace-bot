import datetime

from discord.ext import commands
from discord.utils import oauth_url

from utils.formating import *

from base import BotBase


class Utils(commands.Cog):
    def __init__(self, bot: BotBase) -> None:
        self.bot = bot
    
    def get_uptime(self) -> float:
        uptime = datetime.datetime.now() - self.bot.start_time
        return uptime.total_seconds()

    @commands.hybrid_command(description="Check latency from the bot to discord.com")
    async def ping(self, ctx:commands.Context) -> None:
        await ctx.reply(f"Pong! {round(self.bot.latency*1000)}ms")
    
    @commands.hybrid_command(description="Get install link for your server.")
    @commands.is_owner()
    async def link(self, ctx:commands.Context) -> None:
        if self.bot.application:
            await ctx.reply(oauth_url(self.bot.application.id))
    
    @commands.hybrid_command(description="Get uptime from bot.")
    @commands.is_owner()
    async def uptime(self, ctx:commands.Context) -> None:
        await ctx.reply(f"**Uptime:** {format_time(self.get_uptime())}")

async def setup(bot: BotBase) -> None:
    await bot.add_cog(Utils(bot))