
from fastapi import APIRouter, Depends
from typing import List

import requests
from app.shared.types_common import TenyksResponse

from shared.view_models import Image
from shared.database import get_repository
from .extract import extract
from ..repos.images_repo import ImagesRepository

router = APIRouter(
    prefix="/api/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=TenyksResponse, status_code=201, )
async def post_dataset(request: dict, backend_svc: BackendService=Depends(get_service(BackendService))) -> TenyksResponse:
    """
    On receiving call from interface on this endpoint, route a call to the backend to gather
    all the necessary data to do the extraction
    """
    data = request.get_json()
    
    with requests.session() as s:
        try:
            response = s.get(f"{backend_url}/transaction", json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return json.dumps(err.response.text)
    return response.json()
    response = await datasets_repo.create_dataset(dataset_type, dataset_name, dataset_size, dataset_url)
    
    return dataset