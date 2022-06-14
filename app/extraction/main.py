from .routers import extract
from shared.utils_fastapi import create_app


app = create_app(routers = [extract.router])