from .routers import datasets, models, images
from shared.utils_fastapi import create_app


app = create_app(routers = [datasets.router, models.router, images.router])
