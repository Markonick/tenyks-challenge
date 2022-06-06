
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

@router.get("/{dataset_id}", response_model=Image, status_code=200, )
async def get_dataset_by_id(dataset_id: Image.Key, images_repo: ImagesRepository=Depends(get_repository(ImagesRepository))) -> Image:
    """Get a dataset based on a known dataset id."""

    dataset = await images_repo.get_image_by_id(dataset_id)
    
    return dataset

@router.post("/", response_model=Image, status_code=201, )
async def post_image(image: Image, images_repo: ImagesRepository=Depends(get_repository(ImagesRepository))) -> Image:
    """"Get a dataset based on dataset name."""
    dataset_type = dataset.type
    dataset_name = dataset.name
    dataset_size = dataset.size
    dataset_url = dataset.url
    dataset = await images_repo.create_image(dataset_type, dataset_name, dataset_size, dataset_url)
    
    return dataset