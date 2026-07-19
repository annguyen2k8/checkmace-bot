from discord import Member, Message, TextChannel
from discord.ext import commands

from base import BotBase
from utils.formating import *


class MonitorChat(commands.Cog):
    def __init__(self, bot: BotBase) -> None:
        self.bot = bot
        
        self.config = bot.config["monitor"]
        self.victim_id = self.config["victim_id"]
        
        self.bot.loop.create_task(self.setup_webhook())
    
    async def setup_webhook(self) -> None:
        self.channel = self.bot.get_channel(self.config["channel_id"])
        
        if self.channel and isinstance(self.channel, TextChannel):
            webhooks = await self.channel.webhooks()

            existing = None
            for wh in webhooks:
                if wh.name == self.bot.config.get("webhook_name"):
                    existing = wh
                    break

            if existing:
                self.webhook = existing
            else:
                self.webhook = await self.channel.create_webhook(name=self.bot.config["webhook_name"])
    
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return
        
        if not message.content:
            return
        
        if message.author.id == self.victim_id:
            await self.webhook_send(message)
        
    async def webhook_send(self, message: Message) -> None:
        content = escape(message.content, mass_mentions=True)
        author = message.author
        avatar_url = author.avatar.url if author.avatar else None
        username = author.name
        
        files = []
        
        if isinstance(author, Member):
            username = author.display_name
        
        for attachment in message.attachments:
            file = await attachment.to_file()
            
            files.append(file)
            
            self.bot.logger.info(file.filename)
        
        await self.webhook.send(content, username=username, avatar_url=avatar_url, files=files)


async def setup(bot: BotBase) -> None:
    await bot.add_cog(MonitorChat(bot))