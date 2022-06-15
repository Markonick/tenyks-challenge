import asyncpg, os, logging
from typing import List, Optional, Union, Callable
from pickle import DICT
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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
        user=os.getenv("PSQL_USERNAME"),
        password=os.getenv("PSQL_PASSWORD"),
        host="postgres",
        # port=5432,
        database=os.getenv("PSQL_DATABASE"),
        server_settings={"search_path": os.getenv("PSQL_SCHEMA")}
    )
    
    # logger.info("Connection established")

async def close_db_connection(app: FastAPI) -> None:
    # logger.info("Closing connection to database")

    await app.state.pool.close()

    # logger.info("Connection closed")

def create_app(routers: Optional[List] = None):

    app = FastAPI()

    origins= [os.getenv("")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    # @app.exception_handler(TenyksException)
    async def tenyks_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Oops! did something. Terminator dispatched...{exc}"},
        )
    
    # @app.exception_handler(TenyksRequestValidationError)  
    async def tenyks_validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": f"Request cannot be procesed. Please check your client call...{exc}"},
        )
    if routers:
        [app.include_router(router) for router in routers ]

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))
    app.add_exception_handler(Exception, tenyks_exception_handler)
    app.add_exception_handler(RequestValidationError, tenyks_validation_exception_handler)

    return app