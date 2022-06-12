import json
from fastapi import APIRouter, Depends, Request
from typing import List

from shared.types_common import TenyksImagesRequest, TenyksResponse, TenyksSuccess
from shared.view_models import Annotations, BoundingBox, Category, Image
from ..repos.images_repo import ImagesRepository
from shared.database import get_repository

router = APIRouter(
    prefix="/api/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/all",
    response_model=TenyksResponse,
    status_code=200,
)
async def get_all_images(
    request: TenyksImagesRequest,
    images_repo: ImagesRepository = Depends(get_repository(ImagesRepository)),
) -> TenyksResponse:
    """Get all images in a dataset based on dataset name."""
    dtos = await images_repo.get_all_images(dataset_name=request.dataset_name)

    images = [
        Image(
            # id=dto.id,
            name=dto.name,
            url=dto.images_path,
            dataset_name=dto.dataset_name,
            annotations=Annotations(
                bboxes=[json.loads(bbox) for bbox in dto.bboxes],
                categories=[cat for cat in dto.categories],
            ),
        )
        for dto in dtos
    ]

    return TenyksResponse(response=TenyksSuccess(result=images))


@router.get(
    "/{image_id}",
    response_model=Image,
    status_code=200,
)
async def get_dataset_by_id(
    image_id: int,
    images_repo: ImagesRepository = Depends(get_repository(ImagesRepository)),
) -> Image:
    """Get an image from a dataset based on a known image id."""

    dataset = await images_repo.get_image_by_id(image_id)

    return dataset


@router.post(
    "",
    response_model=Image,
    status_code=201,
)
async def post_image(
    image: Image,
    images_repo: ImagesRepository = Depends(get_repository(ImagesRepository)),
) -> Image:
    """ "Post an image based on the dataset name."""

    annotations = image.annotations
    name = image.name
    dataset_name = image.dataset_name
    dataset = await images_repo.create_image(
        name=name, dataset_name=dataset_name, annotations=annotations
    )

    return dataset
