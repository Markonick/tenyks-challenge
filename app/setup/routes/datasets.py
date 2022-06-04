
from fastapi import APIRouter, Depends
from typing import List

from ...shared.view_models import Dataset
from ..repos.datasets_repo import DatasetsRepository
from ...shared.database import get_repository

router = APIRouter(
    prefix="/api/datasets",
    tags=["datasets"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{dataset_id}", response_model=Dataset, status_code=200, )
async def get_dataset_by_id(dataset_id: Dataset.Key, datasets_repo: DatasetsRepository=Depends(get_repository(DatasetsRepository))) -> Dataset:
    """Get a dataset based on a known dataset id."""

    dataset = await datasets_repo.get_dataset_by_id(dataset_id)
    
    return dataset

@router.get("/{name}", response_model=Dataset, status_code=200, )
async def get_dataset_by_name(name: str, datasets_repo: DatasetsRepository=Depends(get_repository(DatasetsRepository))) -> Dataset:
    """"Get a dataset based on dataset name."""

    dataset = await datasets_repo.get_dataset_by_name(name)
    
    return dataset

@router.post("/", response_model=Dataset, status_code=201, )
async def post_dataset(dataset: Dataset, datasets_repo: DatasetsRepository=Depends(get_repository(DatasetsRepository))) -> Dataset:
    """"Get a dataset based on dataset name."""
    dataset_type = dataset.type
    dataset_name = dataset.name
    dataset_size = dataset.size
    dataset_url = dataset.url
    dataset = await datasets_repo.create_dataset(dataset_type, dataset_name, dataset_size, dataset_url)
    
    return dataset