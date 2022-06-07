
import os
from fastapi import APIRouter, Depends
from typing import List

import requests

from shared.request_handler import request_handler_post
from shared.types_common import TenyksResponse
from shared.view_models import Image
from shared.database import get_repository
from .extract import extract
from ..services.ml_extract_service import ExtractionService

router = APIRouter(
    prefix="/api/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)

backend_base_url = os.environ.get("BACKEND_BASE_URL", 'http://localhost:5000')


@router.post("", response_model=TenyksResponse, status_code=201, )
async def post_dataset(request: dict, extraction_svc: ExtractionService=Depends(ExtractionService)) -> TenyksResponse:
    """
    On receiving an HTTP POST from the SDK user interface on this endpoint, route a 
    call to the backend to gather all the necessary data for the single image for ML extraction
    """
    
    data = request.get_json()
    response = request_handler_post(url=f"{backend_base_url}/models", request=request)
    print(response)
    return data