
from __future__ import annotations
import io
import json
import os
import re
from fastapi import APIRouter, Depends
from typing import List
import requests

from shared.encoders import NumpyEncoder
from shared.s3_utils import s3_download_files, s3_download_file, AwsConfig
from shared.view_models import Annotations, Dataset, Heatmap, Image, Model
from shared.request_handlers import get_async_request_handler, post_async_request_handler
from shared.types_common import TenyksDatasetsRequest, TenyksExtractionRequest, TenyksImagesRequest, TenyksModelImagesRequest, TenyksModelsRequest, TenyksResponse, TenyksSuccess
from ..services.ml_extract_service import ExtractionTypeBase, dispatch_extractor_service

router = APIRouter(
    prefix="/api/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)

backend_base_url = os.environ.get("BACKEND_BASE_URL", 'http://localhost:5000')

awsConfig = AwsConfig(
    endpoint_url=os.environ.get("AWS_ENDPOINT"),
    region_name=os.environ.get("AWS_REGION"),
    aws_access_key_id=os.environ.get("MINIO_ROOT_USER"),
    aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD"),
)

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
    datasets_endpoint = f"{backend_base_url}/datasets"
    datasets_request = TenyksDatasetsRequest(dataset_name=dataset_name)
    datasets_response = await get_async_request_handler(url=datasets_endpoint, request=datasets_request)
    list_of_dataset_dicts = json.loads(datasets_response.text)["response"]["result"]
    datasets = [Dataset(**dataset_dict) for dataset_dict in  list_of_dataset_dicts]
    img_path = datasets[0].images_path
    # dataset_id = datasets[0].id

    ####### Call Models endpoint
    models_endpoint = f"{backend_base_url}/models"
    models_request = TenyksModelsRequest(model_name=model_name)
    models_response = await get_async_request_handler(url=models_endpoint, request=models_request)
    list_of_model_dicts = json.loads(models_response.text)["response"]["result"]

    models = [Model(**model_dict) for model_dict in  list_of_model_dicts]
    # model_id = models[0].id
    
    ####### Call Images endpoint
    images_path = f"{backend_base_url}/images/all"
    images_request = TenyksImagesRequest(dataset_name=dataset_name)
  
    try:
        images_response = await post_async_request_handler(url=images_path, request=images_request)
    except Exception as e:
        print(e)
    
    list_of_image_dicts = json.loads(images_response.text)["response"]["result"]
    images = [Image(**image_dict) for image_dict in  list_of_image_dicts]
    img_path = f"{images[0].url}/{images[0].name}"
    

    # We got the image paths but unfortunately model_data opens them from a location so we need to create this location
    # by downloading to a temp folder
    
    for image in images:
        try:
            img_path = f"{image.url}/{image.name}"
            result = await s3_download_file(aws_config=awsConfig, file_path=img_path)
            ml_result = dispatch_extractor_service(model_id=0, extraction_type=extraction_type, img_path=result.content)
            
        except Exception as e:
            print(e)      
            result = io.BytesIO()

        # Now update model output related image DB tables
        model_images_request = TenyksModelImagesRequest(
            dataset_name=dataset_name,
            heatmap_path='dummy_path_1',
            activations_path="dummy_path_2"
        )
        try:
            images_response = await post_async_request_handler(url=images_path, request=model_images_request)
        except Exception as e:
            print(e)
        
        return TenyksResponse(response=TenyksSuccess(result=ml_result))