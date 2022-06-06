import dataclasses
import json
from asyncio import AbstractEventLoop
import aiohttp
from dataclasses import dataclass
from fastapi import Response


async def request_handler_post(url, request: dataclass) -> dict:
    headers = {"content-type": "application/json"}
    print(request)
    data = json.dumps(dataclasses.asdict(request))
    print(request)
    async with aiohttp.ClientSession() as session: 
        async with session.post( url=url, headers=headers, data=data) as resp:
            result = await resp.text()

    return result

async def request_handler_get(url, request: dataclass) -> dict:
    headers = {"content-type": "application/json"}
    data = json.dumps(dataclass.asdict(request))
  
    async with aiohttp.ClientSession() as session: 
        async with session.post( url=url, headers=headers, params=data) as resp:
            result = await resp.text()

    return result