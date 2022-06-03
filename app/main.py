import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .backend.routers import setup, technicians, summary, studies, assessment
from .events import create_start_app_handler, create_stop_app_handler

def create_app():

    app = FastAPI()

    origins= [os.getenv("USER_BASE_URL")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(setup.router)
    app.include_router(technicians.router)
    app.include_router(summary.router)
    app.include_router(studies.router)
    app.include_router(assessment.router)

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    return app

app = create_app()
