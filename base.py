import asyncio
import datetime
import logging
import logging.handlers
import os
import pathlib
from logging import Logger
from typing import Dict

import discord
from discord.ext import commands
from discord.utils import _ColourFormatter

from utils.formating import *


class BotBase(commands.Bot):
    def __init__(self, config:Dict) -> None:
        intents = discord.Intents.all()
        
        self.start_time = datetime.datetime.now()
        
        super().__init__(
            command_prefix=config.pop('command_prefix', ['!', '?']),
            description=config.pop('description', None),
            intents=intents
        )
        
        self.config = config
        self.logger = set_logger(self)
    
    
    async def setup_hook(self) -> None:
        self.loop.create_task(self.load_cogs())     

    async def load_cogs(self) -> None:
        await self.wait_until_ready()
        
        await asyncio.sleep(0.1)
        
        loaded_cogs = []
        failed_cogs = []
        cogs_directory = pathlib.Path('./cogs')
        
        for folder in cogs_directory.iterdir():
            try:
                cog_name = f"cogs.{folder.name}.main"
                
                await self.load_extension(cog_name)
                
                loaded_cogs.append(cog_name)
                
            except Exception as e:
                self.logger.error(f"Error to load {cog_name} cog")
                self.logger.exception(e)
                
                failed_cogs.append(cog_name)
                
                await asyncio.sleep(5)
        
        self.logger.info(f"Loaded {len(loaded_cogs)} cogs ({len(failed_cogs)} failed)")
        
        await self.sync_commands()
    
    async def sync_commands(self) -> None:
        try:
            sync = await self.tree.sync()
            
            self.logger.info(f"Total {len(sync)} slash commands, {len(self.commands)} normal commands")
        except Exception as error:
            self.logger.error(error)
    
    async def on_ready(self) -> None:
        now = datetime.datetime.now()
        elapsed_time = now - self.start_time
        
        if self.application:
            self.logger.info(f"Logged bot {self.user} (ID: {self.application.id})")
        
        self.logger.info(f"Took {round(elapsed_time.total_seconds()*1000)}ms to start")

    async def on_command_error(self, ctx:commands.Context, error:commands.errors.CommandError):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send("You don't have permission to use this command")
        
        if ctx.author.id == self.owner_id:
            return await ctx.send(box(error))
        
        self.logger.exception(error)
        
        # owner = self.application.owner
        # channel = await owner.create_dm()
        # await channel.send(
        #     f"{box(traceback.format_exc())}\n" + \
        #     f"User: {ctx.author}\n" + \
        #     f"Content: {ctx.message.content}\n" + \
        #     f"Args: {error.args}"
        #     )


def set_logger(bot:BotBase) -> Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    while logger.hasHandlers():    
        logger.setLevel(logging.INFO)

    dpy_handler = logging.StreamHandler()
    
    
    dpy_handler.setFormatter(_ColourFormatter())
    
    logger.addHandler(dpy_handler)
    
    os.makedirs('logs', exist_ok=True)
    fhandler = logging.handlers.RotatingFileHandler(
        filename=f'logs/{bot.start_time.strftime("%Y-%m-%d")}.log',
        maxBytes=10**7,
        backupCount=5
        )
    
    fmt = logging.Formatter(
        '{asctime} {levelname:<8} {module}.{funcName} '
        '{message}',
        datefmt="[%Y-%m-%d %H:%M:%S]",
        style='{'
        )
    
    
    fhandler.setFormatter(fmt)
    logger.addHandler(fhandler)

    return logger

def start_bot(config) -> None:
    bot = BotBase(config)
    
    bot.run(config.pop('token'), log_handler=None)
