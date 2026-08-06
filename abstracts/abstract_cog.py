import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from discord import Color, Embed, Emoji
from discord.ext import commands

from base import BotBase


class AbstractCog(commands.Cog):
    def __init__(self, bot: BotBase) -> None:
        self.bot = bot
        
        self.embed_color = Color.from_str(self.bot.config["embed_color"])
    
    def create_embed(self, 
            title: Optional[Any] = None, 
            url: Optional[Any] = None, 
            description: Optional[Any] = None,
            timestamp: Optional[datetime] = None
            ) -> Embed:
            return Embed(
                color=self.embed_color, 
                title=title,url=url, description=description, timestamp=timestamp
                )
    
    async def setup_emojis(self, path: Path) -> Dict[str, Emoji]:
        emojis = {}
        for image in path.glob("*.png"):
            name = image.stem
            
            emoji = await self.get_emoji(name)
            if not emoji:
                emoji = await self.bot.create_application_emoji(
                    name=name, 
                    image=image.read_bytes()
                )
                
            emojis[name] = emoji
        
        return emojis

    async def get_emoji(self, name: str) -> Optional[Emoji]:
        for emoji in await self.bot.fetch_application_emojis():
            if emoji.name == name:
                return emoji

        return None