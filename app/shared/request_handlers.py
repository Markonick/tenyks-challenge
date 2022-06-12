import dataclasses
import json
from typing import Any
import httpx
from dataclasses import dataclass
from fastapi import Response


async def get_async_request_handler(url, request: dataclass) -> dict:
    headers = {"content-type": "application/json"}
    params = json.dumps(dataclasses.asdict(request))

    async with httpx.AsyncClient( headers=headers, params=params) as client:
        response = await client.get(url=url, headers=headers, params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"Error while requesting {exc.response.text}.")
            print(f"Error while requesting {exc.request.url!r}.")

    return response

async def post_async_request_handler(url, request: dataclass) -> dict:
    headers = {"content-type": "application/json"}
    data = json.dumps(dataclasses.asdict(request))
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, data=data)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"Error while requesting {exc.response.text}.")
            print(f"Error while requesting {exc.request.url!r}.")

    return response