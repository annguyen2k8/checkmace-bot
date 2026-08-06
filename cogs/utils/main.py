import datetime
import zipfile
from io import BytesIO
from pathlib import Path

from aiofiles.tempfile import TemporaryDirectory
from discord import File
from discord.ext import commands
from discord.utils import oauth_url

from abstracts import AbstractCog
from base import BotBase
from utils.formating import *


class Utils(AbstractCog):
    def __init__(self, bot: BotBase) -> None:
        super().__init__(bot)
    
    def get_uptime(self) -> float:
        uptime = datetime.datetime.now() - self.bot.start_time
        return uptime.total_seconds()

    @commands.hybrid_command(description="Check latency from the bot to discord.com")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.reply(f"Pong! {round(self.bot.latency*1000)}ms")
    
    @commands.hybrid_command(description="Get install link for your server")
    @commands.is_owner()
    async def link(self, ctx: commands.Context) -> None:
        if self.bot.application:
            await ctx.reply(oauth_url(self.bot.application.id))
    
    @commands.hybrid_command(description="Get uptime from bot")
    @commands.is_owner()
    async def uptime(self, ctx: commands.Context) -> None:
        await ctx.reply(f"**Uptime:** {format_time(self.get_uptime())}")

    @commands.hybrid_command(description="Download all emojis from application and convert them to .zip file")
    @commands.is_owner()
    async def download_application_emojis(self, ctx: commands.Context) -> None:
        async with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            for emoji in await self.bot.fetch_application_emojis():
                await emoji.save(temp_dir_path.joinpath(f"{emoji.name}.png"))
            
            fp = BytesIO()
            with zipfile.ZipFile(fp, mode="w") as zip_file:
                for file in temp_dir_path.rglob("*"):
                    zip_file.write(file, file.name)

            fp.seek(0)
            
            await ctx.send(
                "Extracted emojis!",
                file=File(fp, "application_emojis.zip")
                )

async def setup(bot: BotBase) -> None:
    await bot.add_cog(Utils(bot))