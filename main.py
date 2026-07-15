import os
import sys
import json
import time
import pathlib
import asyncio
import warnings
import datetime
import traceback

from typing import *

import logging
import logging.handlers
from logging import Logger

import discord
from discord import app_commands
from discord.ext import commands

from utils.formating import *

class Bot(commands.Bot):
    def __init__(self, config:Dict) -> None:
        intents = discord.Intents.all()
        
        self.start_time = datetime.datetime.now()
        super().__init__(
            command_prefix=config.pop('command_prefix', ['!', '?']),
            description=config.pop('description', None),
            intents=intents
        )
        self.config = kwargs['config']
        self.logger = set_logger(self)
    
    async def setup_hook(self) -> None:
        self.loop.create_task(self.load_cogs())     

    async def load_cogs(self) -> None:
        """
        Loads all cogs in folder.
        """
        await self.wait_until_ready()
        await asyncio.sleep(0.1)
        loaded_cogs = []
        failed_cogs = []
        cogs_directory = pathlib.Path('./cogs')
        for cog in cogs_directory.iterdir():
            cog_name = cog.name
            success = False
            while not success:
                try:
                    await self.load_extension(f'cogs.{cog_name}.main')
                    loaded_cogs.append(cog_name)
                    self.logger.info(f"Loaded {cog_name}'s cog")
                    success = True
                except Exception as e:
                    self.logger.error(f"Error to load {cog_name} cog")
                    failed_cogs.append(cog_name)
                    self.logger.exception(e)
                    await asyncio.sleep(5)
        
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
        self.logger.info(f"Logged bot's {self.user} (ID: {self.application.id})")
        self.logger.info(f"Took {round(elapsed_time.total_seconds()*1000)}ms to start")

    async def on_command_error(self, ctx:commands.Context, error:commands.errors.CommandError):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send("You don't have permission to use this command")
        self.logger.exception(error)
        
        # owner = self.application.owner
        # channel = await owner.create_dm()
        # await channel.send(
        #     f"{box(traceback.format_exc())}\n" + \
        #     f"User: {ctx.author}\n" + \
        #     f"Content: {ctx.message.content}\n" + \
        #     f"Args: {error.args}"
        #     )

def set_logger(bot:commands.Bot) -> Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    log_format = logging.Formatter(
        '{asctime} {levelname:<8} {module}.{funcName} '
        '{message}',
        datefmt="[%Y-%m-%d %H:%M:%S]",
        style='{'
        )
    
    dpy_handler = logging.StreamHandler()
    dpy_handler.setFormatter(log_format)
    logger.addHandler(dpy_handler)
    
    fhandler = logging.handlers.RotatingFileHandler(
        filename=f'logs/{bot.start_time.strftime("%Y-%m-%d")}.log',
        maxBytes=10**7,
        backupCount=5
        )
    fhandler.setFormatter(log_format)
    logger.addHandler(fhandler)

    return logger

def start_bot(config) -> None:
    bot = Bot(config)
    bot.run(config.pop('token'), log_handler=None)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    config = json.loads(open('config.json').read())
    
    start_bot(config)