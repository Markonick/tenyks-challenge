
import json
import aioboto3
import os
import re
from fastapi import APIRouter, Depends
from typing import List
import requests

from shared.view_models import Dataset, Image, Model
from shared.request_handlers import get_async_request_handler, post_async_request_handler
from shared.types_common import TenyksDatasetsRequest, TenyksExtractionRequest, TenyksImagesRequest, TenyksModelsRequest, TenyksResponse, TenyksSuccess
from ..services.ml_extract_service import ExtractionTypeBase, dispatch_extractor_service

router = APIRouter(
    prefix="/api/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)

backend_base_url = os.environ.get("BACKEND_BASE_URL", 'http://localhost:5000')


@router.post("", response_model=TenyksResponse, status_code=201, )
async def post_dataset(request: TenyksExtractionRequest) -> TenyksResponse:
    """
    On receiving an HTTP POST from the SDK user interface here, route a 
    call to the backend to gather all the necessary data for the single image for ML extraction
    """

    extraction_type = request.type
    dataset_name = request.dataset_name
    model_name = request.model_name

    ####### Call Datasets endpoint
    datasets_url = f"{backend_base_url}/datasets"
    datasets_request = TenyksDatasetsRequest(dataset_name=dataset_name)
    datasets_response = await get_async_request_handler(url=datasets_url, request=datasets_request)
    list_of_dataset_dicts = json.loads(datasets_response.text)["response"]["result"]
    datasets = [Dataset(**dataset_dict) for dataset_dict in  list_of_dataset_dicts]
    img_path = datasets[0].images_url
    dataset_id = datasets[0].id

    ####### Call Models endpoint
    models_url = f"{backend_base_url}/models"
    models_request = TenyksModelsRequest(model_name=model_name)
    models_response = await get_async_request_handler(url=models_url, request=models_request)
    list_of_model_dicts = json.loads(models_response.text)["response"]["result"]
    models = [Model(**model_dict) for model_dict in  list_of_model_dicts]
    model_id = models[0].id
    
    ####### Call Images endpoint
    images_url = f"{backend_base_url}/images"
    images_request = TenyksImagesRequest(dataset_id=dataset_id)
    # images_response = await get_async_request_handler(url=images_url, request=images_request)
    
    session = aioboto3.Session()
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket('human_dataset')  # <----------------
        async for s3_object in bucket.objects.all():
            print(s3_object)
    
    images_response = await get_async_request_handler(url=images_url, request=images_request)
    print(json.loads(images_response.text))
    list_of_image_dicts = json.loads(images_response.text)["response"]["result"]
    images = [Image(**image_dict) for image_dict in  list_of_image_dicts]
    img_path = f"{images[0].url}{images[0].name}"
    print(img_path)
    print(img_path)
    print(img_path)
    print(img_path)
    print(img_path)
    # ml_result = dispatch_extractor_service(0, extraction_type, img_path=img_path)
    # print(ml_result)
    # return TenyksResponse(response=TenyksSuccess(result=ml_result))