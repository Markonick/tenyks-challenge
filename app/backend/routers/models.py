
import json
from fastapi import APIRouter, Depends
from typing import List

from shared.types_common import TenyksResponse, TenyksSuccess
from shared.view_models import Model
from ..repos.models_repo import ModelsRepository
from shared.database import get_repository

router = APIRouter(
    prefix="/api/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=TenyksResponse, status_code=200, )
async def get_all_models(models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> TenyksResponse:
    """Get a mode based on a known id."""

    dtos = await models_repo.get_all_models()
    models = [
        Model(
            id=int(dto.id),
            name=dto.name,
            datasets=["adasd"]
        )
        for dto in dtos
    ]
    
    return TenyksResponse(response=TenyksSuccess(result=models))

@router.get("/{model_id}", response_model=Model, status_code=200, )
async def get_model_by_id(model_id: int, models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> Model:
    """Get a mode based on a known id."""

    dto = await models_repo.get_model_by_id(model_id)
    model = Model(model_id=dto.id, name=dto.name)
    return model

@router.get("", response_model=Model, status_code=200, )
async def get_model_by_name(name: str, models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> Model:
    """"Get a model based on model name."""

    dto = await models_repo.get_model_by_name(name)
    model = Model(name=dto.name, datasets=[])
    return model

@router.post("", response_model=Model, status_code=201, )
async def post_model(model: Model, models_repo: ModelsRepository=Depends(get_repository(ModelsRepository))) -> Model:
    """"Post a model."""

    name = model.name
    datasets = model.datasets
    model = await models_repo.create_model(name, datasets)
    
    return model