import asyncio
import dataclasses
from re import S
import aioboto3
from dataclasses import dataclass
from email.generator import Generator
import glob
import os, json
from typing import List, Optional
from shared.types_common import ExtractionTypes, TenyksExtractionRequest

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
class AwsConfig:
    endpoint_url: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str


@dataclass
class DatasetGetRequest:
    name: str


@dataclass
class ModelGetRequest:
    name: str


class TenyksSDK():
    def __init__(self,) -> None:
        self._awsConfig = AwsConfig(
            endpoint_url=os.environ.get("AWS_ENDPOINT"),
            region_name=os.environ.get("AWS_REGION"),
            aws_access_key_id=os.environ.get("MINIO_ROOT_USER"),
            aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD"),
        )
        
        self._backend_base_url = os.environ.get("BACKEND_BASE_URL")
        self.extract_base_url = os.environ.get("EXTRACT_BASE_URL")
        
    async def _s3_get_file_count(self, files_path: str, file_type: str) -> str:
        totalCount = 0
      
        bucket = os.environ.get("AWS_BUCKET")
        session = aioboto3.Session()
        async with session.resource("s3", **dataclasses.asdict(self._awsConfig)) as s3:
            bucket = await s3.Bucket(bucket)  
            async for s3_object in bucket.objects.filter(Prefix=files_path):
                if s3_object.key.split(".")[-1] == file_type:
                    totalCount += 1
            
        return totalCount
           
    async def _s3_get_file_type(self, files_path: str) -> str:
        bucket = os.environ.get("AWS_BUCKET")
        session = aioboto3.Session()
        async with session.resource("s3", **dataclasses.asdict(self._awsConfig)) as s3:
            bucket = await s3.Bucket(bucket)     
            async for s3_object in bucket.objects.filter(Prefix=files_path):
                return s3_object.key.split(".")[-1]

    async def _s3_reader(self, files_path: str, file_type_filter: str) -> str:
        bucket = os.environ.get("AWS_BUCKET")
        session = aioboto3.Session()
        async with session.resource("s3", **dataclasses.asdict(self._awsConfig)) as s3:
            bucket = await s3.Bucket(bucket)     
            async for s3_object in bucket.objects.filter(Prefix=files_path):
                if s3_object.key.split(".")[-1] == file_type_filter:
                    yield s3_object.key

    async def dataset(self, name: str) -> Model:

        dataset_request = DatasetGetRequest(name=name)
        resp = await get_async_request_handler(url=f"{self._backend_base_url}/datasets", request=dataset_request)
  
        return resp

    async def save_dataset(self, name: str, dataset_path: str, images_path: str, annotations_path: Optional[str]=None, ):

        dataset_type = await self._s3_get_file_type(files_path=images_path)

        size = await self._s3_get_file_count(files_path=images_path, file_type=dataset_type) 

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

    async def model(self, name: str) -> Model:
        model_request = ModelGetRequest(name=name)
        resp = await get_async_request_handler(url=f"{self._backend_base_url}/models", request=model_request)

        return resp

    async def save_model(self, name: str, datasets: List[str]):
        model_request = Model(name=name, datasets=datasets)
        resp = await post_async_request_handler(url=f"{self._backend_base_url}/models", request=model_request)
        return resp
        
    def image(self) -> Image:
        return self._image

    def image(self, value: Image):
        self._image = value

    def images(self) -> Image:
        return self._image

    async def save_images(self, images_path: str, annotations_path: str):
        
        # annotations_path_gen = os.scandir(annotations_path)
        # images_path_gen = os.scandir(images_path)
        # image_dataset_size = len(glob.glob(images_path))
        # annotations_dataset_size = len(glob.glob(annotations_path))
        try:
            async for i in self._s3_reader(files_path=images_path, file_type_filter='jpg'):
                continue
        except StopAsyncIteration:
            print('YO!')
        while True:
            try:
            
                image_path = next(images_path_gen)
                annotations_path = next(terminator_annotations_path_gen)
                
                if image_dataset_size != annotations_dataset_size:
                    raise(
                        (
                            f"Image and annotation folders contain an unequal number of items!"
                            f"Number of images ({image_dataset_size}) != Number of annotations ({annotations_dataset_size})"
                        )
                    )
                
                bbox_and_categories = load_json(file_path=annotations_path)
                
                image_request = Image(
                    name=str(image_path.name),
                    url=images_path,
                    dataset_name=dataset_name,
                    annotations=Annotations(
                        bboxes=[bbox for bbox in bbox_and_categories['bbox']],
                        categories=[cat for cat in bbox_and_categories['category_id']],
                    )
                )
                
                resp = await post_async_request_handler(url=f"{backend_base_url}/images", request=image_request)
            except StopIteration as ex:
                print(ex)
                return(resp)
            except Exception as ex:
                print(ex)
                print('IMAGES POST  ................Failed')
                raise

    async def extract(self, dataset_name: str, model_name: str, extraction_type: ExtractionTypes):
        request=TenyksExtractionRequest(dataset_name=dataset_name, model_name=model_name, type=extraction_type)
        print(f"{extract_base_url}/extract")
        resp = await post_async_request_handler(url=f"{extract_base_url}/extract", request=request)
        return resp

def load_json(file_path: str) -> dict:

    with open(file_path, "rb") as file:
        result = json.load(file)

    return result

if __name__ == "__main__":
    
    # Initialise Tenyks client 
    ############################################################################################
    tc = TenyksSDK()

    # Run initial setup scripts to get data from sources and push it to DB in internal format 
    ############################################################################################
    
    # Save dataset 1
    dataset_name = "human_dataset"
    human_dataset_base_path = "human_dataset"
    human_images_path = f"{human_dataset_base_path}/images"
    result = asyncio.run(
        tc.save_dataset(
            name=dataset_name,
            dataset_path=human_dataset_base_path,
            images_path=human_images_path,
        )
    )

    # Save dataset 2
    dataset_name = "terminator_dataset"
    terminator_dataset_base_path = "terminator_dataset"
    terminator_images_path = f"{terminator_dataset_base_path}/images"
    result = asyncio.run(
        tc.save_dataset(
            name=dataset_name,
            dataset_path=terminator_dataset_base_path,
            images_path=terminator_images_path,
        )
    )

    # Save model
    model_name = "Humanoid Model 2"
    dataset1_name = "humanoid_datset"
    dataset2_name = "vulcans_dataset"
    result = asyncio.run(
        tc.save_model(
            name=model_name,
            datasets=[dataset1_name, dataset2_name]
        )
    )

    # Save all images in dataset
    dataset_name = "human_dataset"
    human_dataset_base_path = "human_dataset"
    human_images_path = f"{human_dataset_base_path}/images"
    human_annotations_path = f"{human_dataset_base_path}/annotations"
    result = asyncio.run(
        tc.save_images(
            images_path=human_images_path,
            annotations_path=human_annotations_path
        )
    )

    # Now run ML-Extraction (ML-EXTRACT Service) - CPU BOUND, use mulitprocessing, many workers 
    ############################################################################################

    # result = asyncio.run(
    #     tc.extract(dataset_name=dataset_name, model_name=model_name, extraction_type=ExtractionTypes.HEATMAP)
    # )
    # print(result)

    # result = asyncio.run(
    #     tc.extract(extraction_type=ExtractionTypes.ACTIVATIONS)
    # )
    # print(result)

    # result = asyncio.run(
    #     tc.extract(extraction_type=ExtractionTypes.PREDICTIONS)
    # )
    # print(result)
