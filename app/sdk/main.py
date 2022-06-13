import asyncio
import dataclasses
import functools
from re import S
from aiobotocore.session import get_session
from dataclasses import dataclass
import glob
import os, json
from typing import Any, List, Optional

from shared.s3_utils import s3_download_files, s3_get_file_count, s3_get_file_type, AwsConfig
from shared.types_common import ExtractionTypes, ImageSearchFilter, TenyksExtractionRequest, TenyksResponse
from shared.request_handlers import get_async_request_handler, post_async_request_handler
from shared.view_models import (
    Activations, 
    Annotations, 
    BoundingBox, 
    Category, 
    Dataset, 
    Image, 
    Model, 
    Heatmap
)

"""
A client should be able to use the Tenyks SDK in order to perform the following actions:
- Save
- Load
- Extract

On top of that, it should make it as easy as possible for users to discover and use helper utils to get their job done

There are multiple possibilities for the input:
1) Different input folder structure
2) Different data structure to represent annotations: Not only array of arrays but also dictionary, compination of both etc
3) Annotations might not only be bounding boxes but lines, 3d cuboids, landmarks etc so different entity in database and in view_models

Also we must consider being extensible as in the future we might add more metadata at the extraction stage
"""


@dataclass
class DatasetGetRequest:
    name: str


@dataclass
class ModelGetRequest:
    name: str

def force_sync(fn):
    """Turn an async fun to sync"""
    import asyncio

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return asyncio.run(res)
        return res
    return wrapper

class TenyksSDK():
    def __init__(self,) -> None:
        self._awsConfig = AwsConfig(
            endpoint_url=os.environ.get("AWS_ENDPOINT"),
            region_name=os.environ.get("AWS_REGION"),
            aws_access_key_id=os.environ.get("MINIO_ROOT_USER"),
            aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD"),
        )
        
        self._backend_base_url = os.environ.get("BACKEND_BASE_URL")
        self._extract_base_url = os.environ.get("EXTRACT_BASE_URL")

    async def dataset(self, name: str) -> Model:

        dataset_request = DatasetGetRequest(name=name)
        resp = await get_async_request_handler(url=f"{self._backend_base_url}/datasets", request=dataset_request)
  
        return resp

    @force_sync
    async def save_dataset(self, name: str, dataset_path: str, images_path: str, annotations_path: Optional[str]=None, ):

        dataset_type = await s3_get_file_type(aws_config=self._awsConfig, files_path=images_path)

        size = await s3_get_file_count(aws_config=self._awsConfig, files_path=images_path, file_type_filter=dataset_type) 
        dataset_request = Dataset(
            name=name,
            size=size,
            type=dataset_type,
            dataset_path=dataset_path,
            images_path=images_path,
        )
        resp = await post_async_request_handler(url=f"{self._backend_base_url}/datasets", request=dataset_request)
        print(resp)
        return resp

    # async def model(self, name: str) -> Model:
    #     model_request = ModelGetRequest(name=name)
    #     resp = await get_async_request_handler(url=f"{self._backend_base_url}/models", request=model_request)

    #     return resp

    @force_sync
    async def save_model(self, name: str, datasets: List[str]):
        model_request = Model(name=name, datasets=datasets)
        resp = await post_async_request_handler(url=f"{self._backend_base_url}/models", request=model_request)
        print(resp)
        return resp
        
    def image(self) -> Image:
        return self._image

    def image(self, value: Image):
        self._image = value

    def images(self) -> Image:
        return self._image

    @force_sync
    async def save_images(self, dataset_name: str, images_path: str, annotations_path: str):
        
        images_dataset_type = await s3_get_file_type(aws_config=self._awsConfig, files_path=images_path)
        annotations_dataset_type = await s3_get_file_type(aws_config=self._awsConfig, files_path=annotations_path)
        images_dataset_size = await s3_get_file_count(aws_config=self._awsConfig, files_path=images_path, file_type_filter=images_dataset_type) 
        annotations_dataset_size = await s3_get_file_count(aws_config=self._awsConfig, files_path=annotations_path, file_type_filter=annotations_dataset_type)
        responses = []
        if images_dataset_size != annotations_dataset_size:
            raise ValueError(
                (
                    f"Image and annotation folders contain an unequal number of items!"
                    f"Number of images ({images_dataset_size}) != Number of annotations ({annotations_dataset_size})"
                )
            )

        try:
            async for image in s3_download_files(aws_config=self._awsConfig, files_path=annotations_path, file_type_filter='json'):
                bbox_and_categories = image.content
                image_request = Image(
                    name=f"{''.join(image.name.split('.')[:-1])}.{images_dataset_type}",
                    url=images_path,
                    dataset_name=dataset_name,
                    annotations=Annotations(
                        bboxes=[bbox for bbox in bbox_and_categories['bbox']],
                        categories=[cat for cat in bbox_and_categories['category_id']],
                    )
                )
                resp = await post_async_request_handler(url=f"{self._backend_base_url}/images", request=image_request)
                responses.append(resp)
        except StopAsyncIteration:
            pass
        except Exception as ex:
            print(ex)
            print('IMAGES POST  ................Failed')
            raise

        print(responses)
        return responses

    @force_sync
    async def extract(
        self,
        dataset_name: str,
        model_name: str,
        extraction_type: ExtractionTypes,
        image_search_filter: Optional[ImageSearchFilter] = ImageSearchFilter.ALL,
        image_name: Optional[str] = None,
    ) -> TenyksResponse:
        request=TenyksExtractionRequest(
            dataset_name=dataset_name,
            model_name=model_name,
            image_name=image_name, 
            type=extraction_type,
            image_search_filter=image_search_filter
        )
        resp = await post_async_request_handler(url=f"{self._extract_base_url}/extract", request=request)
        print(resp)
        return resp

def load_json(file_path: str) -> dict:
    with open(file_path, "rb") as file:
        result = json.load(file)

    return result

if __name__ == "__main__":
    
    # Initialise Tenyks client 
    ############################################################################################
    tc = TenyksSDK()

   
    # # Save dataset 1
    # dataset_name = "human_dataset"
    # human_dataset_base_path = "human_dataset"
    # human_images_path = f"{human_dataset_base_path}/images"
    # result = tc.save_dataset(
    #     name=dataset_name,
    #     dataset_path=human_dataset_base_path,
    #     images_path=human_images_path,
    # )

    # # Save dataset 2
    # dataset_name = "terminator_dataset"
    # terminator_dataset_base_path = "terminator_dataset"
    # terminator_images_path = f"{terminator_dataset_base_path}/images"
    # result = tc.save_dataset(
    #     name=dataset_name,
    #     dataset_path=terminator_dataset_base_path,
    #     images_path=terminator_images_path,
    # )

    # # Save dataset 3
    # dataset_name = "terminator_dataset2"
    # terminator_dataset_base_path = "terminator_dataset"
    # terminator_images_path = f"{terminator_dataset_base_path}/images"
    # result = tc.save_dataset(
    #     name=dataset_name,
    #     dataset_path=terminator_dataset_base_path,
    #     images_path=terminator_images_path,
    # )

    # # Save model
    # model_name = "Hybrid Model"
    # dataset1_name = "human_dataset"
    # dataset2_name = "terminator_dataset"
    # result = tc.save_model(
    #     name=model_name,
    #     datasets=[dataset1_name, dataset2_name]
    # )

    # # Save model
    # model_name = "Terminator Model"
    # dataset1_name = "terminator_dataset"
    # result = tc.save_model(
    #     name=model_name,
    #     datasets=[dataset1_name]
    # )

    # # Save dataset 3
    # dataset_name = "vulcans_dataset"
    # vulcans_dataset_base_path = "vulcans_dataset"
    # vulcans_images_path = f"{terminator_dataset_base_path}/images"
    # result = tc.save_dataset(
    #     name=dataset_name,
    #     dataset_path=vulcans_dataset_base_path,
    #     images_path=vulcans_images_path,
    # )

    # # Save model
    # model_name = "Humanoid Model 2"
    # dataset1_name = "human_dataset"
    # dataset2_name = "vulcans_dataset"
    # result = tc.save_model(
    #     name=model_name,
    #     datasets=[dataset1_name, dataset2_name]
    # )

    # # Save all images in dataset
    # dataset_name = "human_dataset"
    # human_dataset_base_path = "human_dataset"
    # human_images_path = f"{human_dataset_base_path}/images"
    # human_annotations_path = f"{human_dataset_base_path}/annotations"
    # result = tc.save_images(
    #     dataset_name=dataset_name,
    #     images_path=human_images_path,
    #     annotations_path=human_annotations_path
    # )
    
    # # Save all images in dataset
    # dataset_name = "terminator_dataset"
    # terminator_dataset_base_path = "terminator_dataset"
    # terminator_dataset_images_path = f"{terminator_dataset_base_path}/images"
    # terminator_dataset_annotations_path = f"{terminator_dataset_base_path}/annotations"
    # result = tc.save_images(
    #     dataset_name=dataset_name,
    #     images_path=terminator_dataset_images_path,
    #     annotations_path=terminator_dataset_annotations_path
    # )

    ####### Now run ML-Extraction (ML-EXTRACT Service) - CPU BOUND, use mulitprocessing, many workers 
    #################################################################################################

    # model_name = "Terminator Model"
    # dataset_name = "terminator_dataset"
    # result = tc.extract(
    #     dataset_name=dataset_name,
    #     model_name=model_name,
    #     extraction_type=ExtractionTypes.HEATMAP
    # )

    # model_name = "Hybrid Model"
    # dataset_name = "terminator_dataset"
    # result = tc.extract(
    #     dataset_name=dataset_name,
    #     model_name=model_name,
    #     extraction_type=ExtractionTypes.HEATMAP
    # )


    # model_name = "Terminator Model"
    # dataset_name = "terminator_dataset"
    # image_search_filter = ImageSearchFilter.ALL
    # result = tc.extract(
    #     dataset_name=dataset_name,
    #     model_name=model_name,
    #     image_search_filter=image_search_filter,
    #     extraction_type=ExtractionTypes.PREDICTIONS
    # )

    model_name = "Terminator Model"
    dataset_name = "terminator_dataset"
    image_name = "1.jpg"
    result = tc.extract(
        dataset_name=dataset_name,
        model_name=model_name,
        image_search_filter = ImageSearchFilter.SINGLE,
        image_name=image_name,
        extraction_type=ExtractionTypes.ACTIVATIONS
    )

  
