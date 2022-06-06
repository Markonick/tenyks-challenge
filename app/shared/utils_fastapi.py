import asyncpg, os, logging
from typing import Union, Callable
from pickle import DICT
from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)


def create_start_app_handler(
    app: FastAPI,
) -> Callable:  # type: ignore
    async def start_app() -> None:
        try:
            await connect_to_db(app,)
        except:
            raise("Could not connect to the DB. Is the DB up and running?")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def stop_app() -> None:
        await close_db_connection(app)

    return stop_app

async def connect_to_db(app: FastAPI, ) -> None:
    # logger.info("Connecting to PostgreSQL")
    app.state.pool = await asyncpg.create_pool(
        user=os.getenv('PSQL_USERNAME'),
        password=os.getenv('PSQL_PASSWORD'),
        host='postgres',
        # port=5432,
        database=os.getenv('PSQL_DATABASE'),
        server_settings={'search_path': os.getenv('PSQL_SCHEMA')}
    )

    # logger.info("Connection established")

async def close_db_connection(app: FastAPI) -> None:
    # logger.info("Closing connection to database")

    await app.state.pool.close()

    # logger.info("Connection closed")
