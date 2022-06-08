
import os
from fastapi import APIRouter, Depends
from typing import List
import requests

from shared.request_handlers import post_async_request_handler
from shared.types_common import TenyksExtractionRequest, TenyksResponse
from shared.view_models import Image
from ..services.ml_extract_service import ExtractionTypeBase, dispatch_extractor_service

router = APIRouter(
    prefix="/api/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)

backend_base_url = os.environ.get("BACKEND_BASE_URL", 'http://localhost:5000')


@router.post("", response_model=TenyksResponse, status_code=201, )
async def post_dataset(request: TenyksExtractionRequest, extraction_svc: ExtractionTypeBase=Depends(ExtractionTypeBase)) -> TenyksResponse:
    """
    On receiving an HTTP POST from the SDK user interface here, route a 
    call to the backend to gather all the necessary data for the single image for ML extraction
    """
    type = request.type
    response = await post_async_request_handler(url=f"{backend_base_url}/models", request=request)
    ml_result = dispatch_extractor_service(type)
    print(ml_result)
    return ml_result