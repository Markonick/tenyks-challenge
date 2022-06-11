from dataclasses import dataclass
import json
from fastapi import APIRouter, Depends
from typing import List
from fastapi.encoders import jsonable_encoder

from shared.exception_handlers import TenyksException
from shared.types_common import StatusGroup, TenyksError, TenyksResponse, TenyksSuccess
from shared.view_models import Dataset
from shared.database import get_repository
from ..repos.datasets_repo import DatasetsRepository

router = APIRouter(
    prefix="/api/datasets",
    tags=["datasets"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=TenyksResponse, status_code=200, )
async def get_all_datasets(datasets_repo: DatasetsRepository=Depends(get_repository(DatasetsRepository))) -> TenyksResponse:
    """Get a dataset based on a known dataset id."""

    dtos = await datasets_repo.get_all_datasets()
    
    datasets = [
        Dataset(
            id=int(dto.id),
            name=dto.dataset_name,
            size=dto.dataset_size,
            type=dto.dataset_type_id,
            dataset_path=dto.dataset_path,
            images_path=dto.images_path,
        )
        for dto in dtos
    ]
    
    return TenyksResponse(response=TenyksSuccess(result=datasets))

@router.get("/{dataset_id}", response_model=TenyksResponse, status_code=200, )
async def get_dataset_by_id(dataset_id: int, datasets_repo: DatasetsRepository=Depends(get_repository(DatasetsRepository))) -> Dataset:
    """Get a dataset based on a known dataset id."""

    dto = await datasets_repo.get_dataset_by_id(int(dataset_id))
    dataset = Dataset(
        id=int(dto.id),
        name=dto.dataset_name,
        size=dto.dataset_size,
        type=dto.dataset_type_id,
        dataset_path=dto.dataset_path,
        images_path=dto.images_path,
    )
    return dataset

@router.get("", response_model=TenyksResponse, status_code=200, )
async def get_dataset_by_name(name: str, datasets_repo: DatasetsRepository=Depends(get_repository(DatasetsRepository))) -> Dataset:
    """"Get a dataset based on dataset name."""
 
    try:
        dto = await datasets_repo.get_dataset_by_name(name)
        if not dto:
            return TenyksResponse(
                response=TenyksError(
                    type=StatusGroup.CLIENT_ERROR,
                    message=[]
                )
            )
        else:
            dataset = Dataset(
                id=int(dto.id),
                name=dto.dataset_name,
                size=dto.dataset_size,
                type=dto.dataset_type_id,
                dataset_path=dto.dataset_path,
                images_path=dto.images_path,
            )
    except Exception as e:
        content = f"exception: {e}"
        return TenyksResponse(
            response=TenyksError(
                type=StatusGroup.INTERNAL_ERROR,
                message=content
            )
        )
    
    return TenyksResponse(
        response=TenyksSuccess(
            result=dataset,
            type=StatusGroup.SUCCESS
        )
    )

@router.post("", response_model=TenyksResponse, status_code=201, )
async def post_dataset(
    dataset: Dataset, 
    datasets_repo: DatasetsRepository=Depends(
        get_repository(DatasetsRepository)
    )
) -> Dataset:
    """"Get a dataset based on dataset name."""
    
    dataset_type = dataset.type
    dataset_name = dataset.name
    dataset_size = int(dataset.size)
    dataset_path = dataset.dataset_path
    images_path = dataset.images_path
    
    dataset = await datasets_repo.create_dataset(
        dataset_type=dataset_type,
        dataset_name=dataset_name,
        dataset_size=dataset_size,
        dataset_path=dataset_path,
        images_path=images_path,
    )
    
    return dataset