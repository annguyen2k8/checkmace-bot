import asyncio
from typing import List

from mcstatus import BedrockServer, JavaServer
from mcstatus.responses.bedrock import BedrockStatusResponse
from mcstatus.responses.java import JavaStatusResponse


async def handle_java(host: str) -> JavaStatusResponse:
    server = await JavaServer.async_lookup(host)
    return await server.async_status()


async def handle_bedrock(host: str) -> BedrockStatusResponse:
    server = BedrockServer.lookup(host)
    return await server.async_status()

async def get_status(host: str) -> JavaStatusResponse | BedrockStatusResponse:
    tasks: List[asyncio.Task[JavaStatusResponse | BedrockStatusResponse]] = [
        asyncio.create_task(handle_java(host)),
        # asyncio.create_task(handle_bedrock(host)), # support soon!
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

if __name__ == "__main__":
    import base64
    from io import  BytesIO
    from PIL import Image
    
    response = asyncio.run(get_status("ember.pikamc.vn:25740"))
        
    print(f"{response.latency:.0f}")
    
    if isinstance(response, JavaStatusResponse) and response.icon:
        fp = base64.b64decode(response.icon.split(",")[1])
    
    Image.open(BytesIO(fp)).show()
    
    