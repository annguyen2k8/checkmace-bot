from typing import Any, List, Optional

from discord import (CategoryChannel, Color, Embed, Interaction, Member,
                     TextChannel, VoiceChannel, app_commands)
from discord.ext import commands

from base import BotBase
from utils.formating import box, escape


class RatChat(commands.Cog):
    def __init__(self, bot: BotBase) -> None:
        self.bot = bot
        
        self.embed_color = Color.from_str(self.bot.config["embed_color"])
        
        self.config = self.bot.config["ratchat"]
        
        self.emojis = self.config["emojis"]
    
    def create_embed(self, 
        title: Optional[Any] = None, 
        url: Optional[Any] = None, description: Optional[Any] = None
        ) -> Embed:
        return Embed(
            color=self.embed_color, url=url, description=description
            )
        
    @app_commands.command()
    @commands.is_owner()
    async def guildlist(self, interaction: Interaction) -> None:
        embeds: List[Embed] = []
        for guild in self.bot.guilds:
            embed = self.create_embed(
                ).set_author(
                    name=f"{guild.name}",
                    icon_url=guild.icon.url if guild.icon else None
                )
            
            embed.add_field(name="guild.id", value=box(guild.id))
            
            owner = guild.owner
            if owner:
                embed.set_footer(
                    text=f"{owner.name}",
                    icon_url=owner.avatar.url if owner.avatar else None
                )
                
                embed.add_field(name="owner.id", value=box(owner.id))
            
            embeds.append(embed)
        
        await interaction.response.send_message(embeds=embeds)
    
    @app_commands.command()
    @commands.is_owner()
    async def channelist(self, interaction: Interaction, guild: str) -> None:
        selected_guild = self.bot.get_guild(int(guild))
        if not selected_guild:
            await interaction.response.send_message("Server not found!")
            
            return
        
        lines = []
        categories = sorted(selected_guild.categories, key=lambda c: c.position)
        for category in categories:
            category_channels = sorted(
                [c for c in selected_guild.channels if c.category_id == category.id],
                key=lambda c: (c.position, c.name)
            )
            if not category_channels:
                continue

            lines.append(f"{self.emojis['category']} {category.name}")
            
            for channel in category_channels:
                prefix = "** **" + " "
                if isinstance(channel, TextChannel):
                    lines.append(f"{prefix}\u200b    {self.emojis['text_channel']} {channel.name}")
                elif isinstance(channel, VoiceChannel):
                    if channel.members:
                        lines.append(f"{prefix}\u200b    {self.emojis['voice_channel_online']} {channel.name}")
                        member_prefix = prefix + " " * 10

                        for user_id, state in channel.voice_states.items():
                            voice_status = []

                            if state.self_mute or state.mute:
                                voice_status.append(self.emojis["mute"])

                            if state.self_deaf or state.deaf:
                                voice_status.append(self.emojis["deafened"])

                            if getattr(state, "self_stream", False):
                                voice_status.append(self.emojis["live"])

                            member = selected_guild.get_member(user_id)
                            if member is None:
                                continue

                            status_text = f" {' '.join(voice_status)}" if voice_status else ""
                            lines.append(f"{member_prefix}**{member.display_name}**{status_text}")
                    else:
                        lines.append(f"{prefix}\u200b    {self.emojis['voice_channel']} {channel.name}")
                        
        uncategorized = sorted(
            [c for c in selected_guild.channels if c.category is None and not isinstance(c, CategoryChannel)],
            key=lambda c: (c.position, c.name)
        )
        if uncategorized:
            
            if lines:
                lines.append("")
                
            lines.append(f"{self.emojis['category']} Uncategorized")
            for channel in uncategorized:
                
                if isinstance(channel, TextChannel):
                    lines.append(f"\u200b    {self.emojis['text_channel']} {channel.name}")
                
                elif isinstance(channel, VoiceChannel):
                    lines.append(f"\u200b    {self.emojis['voice_channel']} {channel.name}")

        embed = self.create_embed(
                description="\n".join(lines)
            ).set_author(
                name=f"{selected_guild.name}",
                icon_url=selected_guild.icon.url if selected_guild.icon else None,
                
            )
        
        await interaction.response.send_message(embed=embed)
    
    
    @app_commands.command()
    @commands.is_owner()
    async def history(self, interaction: Interaction, guild: str, channel: str, limit: Optional[int]) -> None:
        if not isinstance(interaction.channel, TextChannel):
            await interaction.response.send_message("This command must be used in a text channel.")
            return

        # Defer the response because this command can take some time
        await interaction.response.defer(ephemeral=True)

        selected_guild = self.bot.get_guild(int(guild))
        if not selected_guild:
            await interaction.response.send_message("Server not found!")
            
            return

        selected_channel = selected_guild.get_channel(int(channel))
        if selected_channel is None:
            await interaction.response.send_message("Channel not found!")
            return

        if not (isinstance(selected_channel, TextChannel) or isinstance(selected_channel, VoiceChannel)):
            await interaction.response.send_message("Selected channel is not supported.")
            return

        webhook = await interaction.channel.create_webhook(name=self.bot.config["webhook_name"])
        previous_message = None
        async for message in selected_channel.history(limit=limit, oldest_first=False):
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

            if (
                previous_message is None
                or previous_message.author != message.author
                or (message.created_at - previous_message.created_at).total_seconds() >= 180
            ):
                timestamp = message.created_at.strftime("%d-%m-%Y %H:%M:%S")
                content = f"-# {timestamp} \n{content}" if content else f"-# {timestamp}"

            await webhook.send(content, username=username, avatar_url=avatar_url, files=files)
            previous_message = message

            
        await webhook.delete()
        await interaction.followup.send("Done!", ephemeral=True)
        
    @channelist.autocomplete("guild")
    @history.autocomplete("guild")
    async def guild_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        return [
            app_commands.Choice(name=guild.name, value=str(guild.id)) 
            for guild in self.bot.guilds if current.lower() in guild.name.lower()
        ][:25]
    
    @history.autocomplete("channel")
    async def channel_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        selected_guild = self.bot.get_guild(int(interaction.namespace.guild))
        
        if not selected_guild:
            return []
        
        return [
            app_commands.Choice(name=channel.name, value=str(channel.id)) 
            for channel in selected_guild.channels if current.lower() in channel.name.lower()
            and not isinstance(channel, CategoryChannel)
        ]

async def setup(bot: BotBase) -> None:
    await bot.add_cog(RatChat(bot))
    