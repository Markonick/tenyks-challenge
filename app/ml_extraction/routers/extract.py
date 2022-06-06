
from fastapi import APIRouter, Depends
from typing import List

from shared.view_models import Image
from shared.database import get_repository
from .extract import extract
from ..repos.images_repo import ImagesRepository

router = APIRouter(
    prefix="/api/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Image)
async def root():
    try:
        result = await extract()
        return ComponentResponse[Response](
            jobId=component_request.jobId,
            response=ComponentSuccess[Response](result=result),
        ).dict()

    except Exception as e:
        print(e)
        e.body = jsonable_encoder(component_request)
        raise
