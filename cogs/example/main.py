import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import oauth_url

from utils.formating import *

class ExampleCog(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
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
        await ctx.reply(oauth_url(self.bot.application_id))
    
    @commands.hybrid_command(description="Get uptime from bot.")
    @commands.is_owner()
    async def uptime(self, ctx:commands.Context) -> None:
        await ctx.reply(f"**Uptime:** {format_time(self.get_uptime())}")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(ExampleCog(bot))