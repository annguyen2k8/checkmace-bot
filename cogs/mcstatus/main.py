
from pathlib import Path

from discord import File
from discord.ext import commands
from PIL import Image
from io import BytesIO

from abstracts import AbstractCog
from base import BotBase

from .server import get_status
from mcstatus.responses import JavaStatusResponse, JavaStatusPlayers
import base64
ASSETS_PATH = Path(__file__).parent.joinpath("assets")

IMAGES = {
    path.stem: Image.open(path) for path in ASSETS_PATH.glob("*.png")
}

class StatusIcons:
    thresholds = [
        (150 ,  "ping_5"),
        (300 ,  "ping_4"),
        (600 ,  "ping_3"),
        (1000,  "ping_2"),
    ]
    highping = "ping_1"
    unreachable = "unreachable"

    @classmethod
    def from_latency(cls, latency: float) -> str:
        for threshold, emoji_name in cls.thresholds:
            if latency < threshold:
                return emoji_name
        
        return cls.highping

class MCstatus(AbstractCog):
    assets_dir = Path(__file__).parent / "assets"
    def __init__(self, bot: BotBase) -> None:
        super().__init__(bot)
    
    async def cog_load(self) -> None:
        self.emojis = await self.setup_emojis(self.assets_dir / "emoji")
    
    @commands.hybrid_command()
    async def mcping(self, ctx: commands.Context, address: str) -> None:
        failed = False
        try:
            response = await get_status(address)
        except ValueError:
            failed = True
            
        embed = self.create_embed()

        fp = self.assets_dir / "default_icon.png"
        if isinstance(response, JavaStatusResponse) and response.icon:
            fp = BytesIO(base64.b64decode(response.icon.split(",")[1]))
        
        file = File(fp, "icon.png")
        
        embed.set_author(name=address, icon_url=file.uri)
        
        if not failed:
            players = response.players
            
            name = f"Players ({players.online}/{players.max})"
            value = "** **"
            
            players = response.players
            if isinstance(players, JavaStatusPlayers) and players.sample:
                value = "\n".join(map(lambda p: f"**{p.name}** `{p.uuid}`", players.sample))
        
            embed.add_field(name=name, value=value)
        
        value = f"{self.emojis[StatusIcons.unreachable]} No connection!"
        if not failed:
            latency = response.latency
            
            value = f"`{latency:.0f}ms` {self.emojis[StatusIcons.from_latency(latency)]}"

        embed.add_field(name="Latency", value=value)
        
        await ctx.reply(embed=embed, file=file)
        
async def setup(bot: BotBase) -> None:
    await bot.add_cog(MCstatus(bot))