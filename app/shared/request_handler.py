import dataclasses
import json
import httpx
from dataclasses import dataclass
from fastapi import Response


async def request_handler_post(url, request: dataclass) -> dict:
    headers = {"content-type": "application/json"}
    data = json.dumps(dataclasses.asdict(request))

    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, data=data)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"Error while requesting {exc.request.url!r}.")

    return response

async def request_handler_get(url, request: dataclass) -> dict:
    headers = {"content-type": "application/json"}
    data = json.dumps(dataclass.asdict(request))
  
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers, params=data)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"Error while requesting {exc.request.url!r}.")

    return response