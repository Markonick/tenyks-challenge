
from fastapi import APIRouter, Depends
from typing import List

from shared.view_models import Image
from ..repos.images_repo import ImagesRepository
from shared.database import get_repository

router = APIRouter(
    prefix="/api/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{image_id}", response_model=Image, status_code=200, )
async def get_dataset_by_id(image_id: int, images_repo: ImagesRepository=Depends(get_repository(ImagesRepository))) -> Image:
    """Get a dataset based on a known dataset id."""

    dataset = await images_repo.get_image_by_id(image_id)
    
    return dataset

@router.post("/", response_model=Image, status_code=201, )
async def post_image(image: Image, images_repo: ImagesRepository=Depends(get_repository(ImagesRepository))) -> Image:
    """"Get a dataset based on dataset name."""
    
    annotations = image.annotations
    name = image.name
    dataset_name = image.dataset_name
    image_url = image.dataset_name
    dataset = await images_repo.create_image(name=name, dataset_name=dataset_name, annotations=annotations, url=image_url)
    
    return dataset