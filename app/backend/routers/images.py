import json
import re
from fastapi import APIRouter, Depends, Request
from typing import List, Optional

from shared.types_common import ExtractionTypes, TenyksImagesRequest, TenyksModelImagesRequest, TenyksResponse, TenyksSuccess
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
            id=dto.id,
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


# @router.get(
#     "/{image_id}",
#     response_model=Image,
#     status_code=200,
# )
# async def get_image_by_id(
#     image_id: int,
#     images_repo: ImagesRepository = Depends(get_repository(ImagesRepository)),
# ) -> Image:
#     """Get an image from a dataset based on a known image id."""

#     image = await images_repo.get_image_by_id(image_id)

#     return image

@router.get(
    "",
    response_model=TenyksResponse,
    status_code=200,
)
async def get_dataset_by_name(
    dataset_name: str,
    image_name: Optional[str] = None,
    images_repo: ImagesRepository = Depends(get_repository(ImagesRepository)),
) -> TenyksResponse:
    """Get an image from a dataset based on a known image id."""
    
    image_dto = await images_repo.get_image_by_name(image_name)
    print(image_dto)
    print(image_dto)
    print(image_dto)
    print(image_dto)
    return TenyksResponse(
        response=TenyksSuccess(
            result=Image(
                id=image_dto.id,
                name=image_dto.name,
                url=image_dto.images_path,
                dataset_name=image_dto.dataset_name,
                annotations=Annotations(
                    bboxes=[json.loads(bbox) for bbox in image_dto.bboxes],
                    categories=image_dto.categories,
                ),
            )
        )
    )


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

@router.post(
    "/model",
    response_model=Image,
    status_code=201,
)
async def post_image(
    request: TenyksModelImagesRequest,
    images_repo: ImagesRepository = Depends(get_repository(ImagesRepository)),
) -> Image:
    """ "Post an image based on the dataset name."""

    image_id = request.image_id
    path_to_extraction_result = request.result_path
    dataset_name = request.dataset_name
    model_annotations = request.model_annotations
    extraction_type = request.extraction_type
    model_name = request.model_name
    print(model_annotations)
    print(model_annotations)
    print(model_annotations)
    print(model_annotations)
    if extraction_type == ExtractionTypes.PREDICTIONS:
        dataset = await images_repo.create_model_image_annotations(
            image_id=image_id, model_name=model_name, model_annotations=model_annotations
        )
    elif extraction_type == ExtractionTypes.HEATMAP:
        dataset = await images_repo.create_model_image_heatmap(
            image_id=image_id, model_name=model_name, result_path=path_to_extraction_result
        )
    elif extraction_type == ExtractionTypes.ACTIVATIONS:
        dataset = await images_repo.create_model_image_activations(
            image_id=image_id, model_name=model_name, result_path=path_to_extraction_result
        )
    else:
        raise("Extraction type doesn't exist")

    return dataset
