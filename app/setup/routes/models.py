
from fastapi import APIRouter, Depends
from typing import List

from ...shared.view_models import Model
from ..repos.images_repo import ModelsRepository
from ...shared.database import get_repository

router = APIRouter(
    prefix="/api/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{model_id}", response_model=Model, status_code=200, )
async def get_model_by_id(model_id: Model.Key, models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> Model:
    """Get a mode based on a known id."""

    model = await models_repo.get_model_by_id(model_id)
    
    return model

@router.get("/{name}", response_model=Model, status_code=200, )
async def get_model_by_name(name: str, models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> Model:
    """"Get a model based on model name."""

    model = await models_repo.get_model_by_name(name)
    
    return model

@router.post("/", response_model=Model, status_code=201, )
async def post_model(name: str, models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> Model:
    """"Get a dataset based on dataset name."""
    model = await models_repo.create_model(name)
    
    return model