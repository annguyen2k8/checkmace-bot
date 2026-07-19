import asyncio
from tempfile import TemporaryFile
from typing import List

from discord.ext import commands
from mcstatus import BedrockServer, JavaServer
from mcstatus.responses.bedrock import BedrockStatusResponse
from mcstatus.responses.java import JavaStatusResponse

from base import BotBase


async def handle_java(host: str) -> JavaStatusResponse:
    server = await JavaServer.async_lookup(host)
    return await server.async_status()


async def handle_bedrock(host: str) -> BedrockStatusResponse:
    server = BedrockServer.lookup(host)
    return await server.async_status()


async def status(host: str) -> JavaStatusResponse | BedrockStatusResponse:
    tasks: List[asyncio.Task[JavaStatusResponse | BedrockStatusResponse]] = [
        asyncio.create_task(handle_java(host)),
        asyncio.create_task(handle_bedrock(host)),
    ]

    try:
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
            except Exception:
                continue
            else:
                for t in tasks:
                    if t is not task:
                        t.cancel()
                return result
    finally:
        for t in tasks:
            t.cancel()

    raise ValueError("No tasks were successful. Is the server offline?")

class MCstatus(commands.Cog):
    def __init__(self, bot: BotBase) -> None:
        self.bot = bot
    
    @commands.hybrid_command()
    async def mcstatus(self, ctx: commands.Context, address: str) -> None:
        response = await status(address)
        
        


async def setup(bot: BotBase) -> None:
    await bot.add_cog(MCstatus(bot))