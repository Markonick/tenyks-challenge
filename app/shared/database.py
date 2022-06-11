from dataclasses import dataclass, is_dataclass, fields
import pydantic
from typing import AsyncGenerator, Callable, Type, List, TypeVar
import asyncpg
from asyncpg.connection import Connection
from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request

T = TypeVar("T")

class Config:
    arbitrary_types_allowed = True

@pydantic.dataclasses.dataclass(config=Config)
class BaseRepository:
    conn: Connection

    @property
    def connection(self) -> Connection:
        return self.conn


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool

async def _get_connection_from_pool(
    pool: Pool = Depends(_get_db_pool),
) -> AsyncGenerator[Connection, None]:
    async with pool.acquire() as conn:
        yield conn

def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[Connection], BaseRepository]:
    def _get_repo(
        conn: Connection = Depends(_get_connection_from_pool),
    ) -> BaseRepository:
        return repo_type(conn)

    return _get_repo
    
async def typed_fetch(conn: Connection, typ: T, query: str, *args) -> List[T]:
    """Maps all columns of a database record to a Python data class."""

    if not is_dataclass(typ):
        raise TypeError(f"{typ} must be a dataclass type or List[dataclass] type")

    records = await conn.fetch(query, *args)
    return _typed_fetch(typ, records)

def _typed_fetch(typ: Type[T], records: List[asyncpg.Record]) -> List[T]:
    results = []

    for record in records:
        result = object.__new__(typ)
        if is_dataclass(typ):
            for field in fields(typ):
                key = field.name
                value = record.get(key, None)

                if value is not None:
                    setattr(result, key, value)
                elif field.default:
                    setattr(result, key, field.default)
                # else:
                #     raise RuntimeError(
                #         f"object field {key} without default value is missing a corresponding database record column"
                #     )
        else:
            for key, value in record.items():
                setattr(result, key, value)
        results.append(result)
    return results