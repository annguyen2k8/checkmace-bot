import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from utils.formating import *

from base import BotBase


class MonitorChat(commands.Cog):
    def __init__(self, bot: BotBase) -> None:
        self.bot = bot
        
        self.config = bot.config["monitor"]
        
        self.bot.loop.create_task(self.setup_webhook())
    
    async def setup_webhook(self) -> None:
        self.channel = self.bot.get_channel(self.config["channel_id"])
        
        if self.channel and isinstance(self.channel, discord.TextChannel):
            webhooks = await self.channel.webhooks()

            existing = None
            for wh in webhooks:
                if wh.name == self.config.get("webhook_name"):
                    existing = wh
                    break

            if existing:
                self.webhook = existing
            else:
                self.webhook = await self.channel.create_webhook(name=self.config["webhook_name"])
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        
        author = message.author
        avatar_url = author.avatar.url if author.avatar else None
        
        username = author.name
        if isinstance(author, discord.Member):
            username = author.display_name
        
        await self.webhook.send(message.content, username=username, avatar_url=avatar_url)

            
            

async def setup(bot: BotBase) -> None:
    await bot.add_cog(MonitorChat(bot))