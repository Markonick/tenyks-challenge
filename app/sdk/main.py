import asyncio
from dataclasses import dataclass
from email.generator import Generator
import glob
import os, json
from typing import List
from shared.types_common import TenyksExtractionRequest

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

class TenyksSDK():
    def __init__(self,) -> None:
        pass

    @property
    async def dataset(self, name: str) -> Model:

        dataset_request = DatasetGetRequest(name=name)
        resp = await get_async_request_handler(url=f"{base_url}/datasets", request=dataset_request)
  
        return resp

    async def save_dataset(self, name: str, images_path: str, annotations_path: str, dataset_path: str):

        annotations_dataset_size = len(glob.glob(annotations_path))
        images_path_gen = os.scandir(images_path)
        image_path = next(images_path_gen).name
        # Assumption/Trade-off (could be wrong): All image types within a dataset are of a single type eg. jpg
       
        dataset_type = str(image_path).split(".")[-1]

        dataset_request = Dataset(name=name, size=annotations_dataset_size, type=dataset_type, url=dataset_path)
        resp = await post_async_request_handler(url=f"{base_url}/datasets", request=dataset_request)

        return resp

    @property
    async def model(self, name: str) -> Model:
        model_request = ModelGetRequest(name=name)
        resp = await get_async_request_handler(url=f"{base_url}/models", request=model_request)

        return resp

    @model.setter
    async def model(self, name: str, datasets: List[int]):
        model_request = Model(name=name, datasets=datasets)
        resp = await post_async_request_handler(url=f"{base_url}/models", request=model_request)
        return resp
        
    @property
    def image(self) -> Image:
        print('property image called')
        return self._image

    @image.setter
    def image(self, value: Image):
        print('property.setter image called')
        self._image = value

    @property
    def images(self) -> Image:
        print('property images called')
        return self._image

    @images.setter
    async def images(self, images_path: str, annotations_path: str):
        print('property.setter images called')
        
        annotations_path_gen = os.scandir(annotations_path)
        images_path_gen = os.scandir(images_path)
        image_dataset_size = len(glob.glob(images_path))
        annotations_dataset_size = len(glob.glob(annotations_path))

        while True:
            try:
            
                image_path = next(annotations_path_gen)
                annotations_path = next(terminator_annotations_path_gen)

                if image_dataset_size != images_path_gen:
                    raise(
                        (
                            f"Image and annotation folders contain an unequal number of items!"
                            f"Number of images ({image_dataset_size}) != Number of annotations ({annotations_dataset_size})"
                        )
                    )
                
                bbox_and_categories = load_json(file_path=annotations_path)
                
                image_request = Image(
                    name=str(image_path.name),
                    dataset_name=dataset_name,
                    url=str(image_path),
                    annotations=Annotations(
                        bboxes=[BoundingBox(array=bbox) for bbox in bbox_and_categories['bbox']],
                        categories=[Category(category_id=cat) for cat in bbox_and_categories['category_id']],
                    )
                )
                
                resp = await post_async_request_handler(url=f"{base_url}/images", request=image_request)
                print('IMAGE POST  ................Complete')
            except StopIteration:
                break
            except Exception as ex:
                print(ex)
                print('IMAGE POST  ................Failed')
            return resp

    async def extract(self, extraction_type):
        print("select")
        resp = await post_async_request_handler(url=f"{extract_url}/extract", request=TenyksExtractionRequest(type=extraction_type))
        return resp

def load_json(file_path: str) -> dict:

    with open(file_path, "rb") as file:
        result = json.load(file)

    return result

if __name__ == "__main__":
    
    # Set inputs (UI Service) ##################################################################
    ############################################################################################
    
    human_dataset_base_path = "./sdk/dataset_data/human_dataset"
    human_annotations_path = f"{human_dataset_base_path}/annotations/"
    human_images_path = f"{human_dataset_base_path}/images/"

    terminator_dataset_base_path = "./sdk/dataset_data/terminator_dataset"
    terminator_annotations_path = f"{terminator_dataset_base_path}/annotations/"
    terminator_images_path = f"{terminator_dataset_base_path}/images/"
    
    human_annotations_path_gen = os.scandir(human_annotations_path)
    human_images_path_gen = os.scandir(human_images_path)

    terminator_annotations_path_gen = os.scandir(terminator_annotations_path)
    terminator_images_path_gen = os.scandir(terminator_images_path)

    model_id = 0
    dataset_name_human = "human_dataset"
    dataset_name_terminator = "terminator_dataset"
    model_name = "Humanoid Model"

    
    # Persist dataset data into DB (BACKEND Service) - IO BOUND, use async #####################
    ############################################################################################
    base_url = "http://backend:8000/api"
    extract_url = "http://extract:8000/api"
    dataset_name = 'terminator_dataset'
    dataset_type = 'jpg'
    dataset_url = human_images_path
    dataset_size = len(list(os.scandir(dataset_url)))
    image_dataset_size = len(glob.glob(human_images_path))
    annotations_dataset_size = len(glob.glob(human_annotations_path))
    
   

    tc = TenyksSDK()

    result = asyncio.run(
        tc.save_dataset(
            name=dataset_name,
            images_path=human_images_path,
            annotations_path=human_annotations_path,
            dataset_path=human_dataset_base_path
        )
    )
    print(result)
    # Now run ML-Extraction (ML-EXTRACT Service) - CPU BOUND, use mulitprocessing, many workers 
    ############################################################################################


    # Save ML outputs internal API format into DB (BACKEND Service) - IO BOUND, use async ######
    ############################################################################################
    
    # print(heatmap)
    # print(bbox_and_categories)
    # print(activations)
    # print(activations_vm.array)