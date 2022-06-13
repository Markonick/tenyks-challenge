
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
from shared.view_models import Annotations, Image
from shared.request_handlers import get_async_request_handler, post_async_request_handler
from shared.types_common import (
    ExtractionTypes,
    ImageSearchFilter,
    StatusGroup,
    TenyksError,
    TenyksExtractionRequest,
    TenyksImagesRequest,
    TenyksModelImagesRequest,
    TenyksResponse,
    TenyksSuccess,
)
from ..services.ml_extract_service import dispatch_extractor_service

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
    image_search_filter = request.image_search_filter
    image_name = request.image_name

    ################# Call /images/all or images/{name} endpoint
    images_endpoint = f"{backend_base_url}/images"
    images_request = TenyksImagesRequest(dataset_name=dataset_name, image_name=image_name)
  
    try:
        if image_search_filter == ImageSearchFilter.ALL:
            url = f"{images_endpoint}/{image_search_filter}"
            images_response = await post_async_request_handler(url=url, request=images_request)
        elif image_search_filter == ImageSearchFilter.SINGLE:
            images_response = await get_async_request_handler(url=images_endpoint, request=images_request)
        else:
            raise "Unknown search filter {image_search_filter}"
    except Exception as e:
        print(e)
        images_response = []
    
    list_of_image_dicts = json.loads(images_response.text)["response"]["result"]
    print(list_of_image_dicts)
    print(type(list_of_image_dicts["annotations"]["bboxes"]))
    print(type(list_of_image_dicts["annotations"]["bboxes"][0]))
    images = [
        Image(
            name=image_dict["name"],
            url=image_dict["url"],
            dataset_name=image_dict["dataset_name"],
            annotations=image_dict["annotations"],

        ) 
        for image_dict in  list_of_image_dicts
    ]

    img_path = f"{images[0].url}/{images[0].name}"
    

    ################# We got the image paths so do the actual ML processing...
    
    for image in images:
        try:
            img_path = f"{image.url}/{image.name}"
            result = await s3_download_file(aws_config=awsConfig, file_path=img_path)

            # Can be any of annotations(bboxes+categories), heatmap or activations
            ml_extraction_result = dispatch_extractor_service(
                model_id=0,
                extraction_type=extraction_type,
                img_path=result.content
            )
            
        except Exception as e:
            print(e)      
            result = io.BytesIO()

        # Now update model output related image DB tables
        model_images_request = TenyksModelImagesRequest(
            image_id=image.id,
            model_name=model_name,
            dataset_name=dataset_name,
            extraction_type=extraction_type,
            result_path='dummy_path_1',
            model_annotations=Annotations(
                bboxes=[bbox for bbox in ml_extraction_result['bbox']],
                categories=[cat for cat in ml_extraction_result['category_id']],
            ) if extraction_type==ExtractionTypes.PREDICTIONS else None
        )
        try:
            # Call to /images/model endpoint#    
            model_images_endpoint = f"{images_endpoint}/model"
            images_response = await post_async_request_handler(url=model_images_endpoint, request=model_images_request)
        except Exception as e:
            print(e)
            TenyksResponse(
                response=TenyksError(
                    message="There was an error with the request: {e}",
                    type= StatusGroup.INTERNAL_ERROR
                )
            )
        return TenyksResponse(response=TenyksSuccess(result=ml_extraction_result))