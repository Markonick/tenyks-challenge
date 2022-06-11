import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from shared.exception_handlers import TenyksException, TenyksRequestValidationError
from .routers import extract

from shared.utils_fastapi import create_start_app_handler, create_stop_app_handler

def create_app():

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

    app.include_router(extract.router)

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))
    app.add_exception_handler(Exception, tenyks_exception_handler)
    app.add_exception_handler(RequestValidationError, tenyks_validation_exception_handler)

    return app
    
app = create_app()
