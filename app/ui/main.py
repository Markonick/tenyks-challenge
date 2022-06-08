from dataclasses import dataclass
import glob
import os, json
from typing import List
from asyncio import get_event_loop

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
from shared.model_data import DummyModel

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

class TenyksSDK():
    def __init__(self,) -> None:
        self._dataset = ""
        self._model = ""
        self._image = ""

    @property
    async def dataset(self, name: str) -> Model:
        @dataclass
        dataset_request = Dataset(name=name)
        resp = await get_async_request_handler(url=f"{base_url}/datasets", request=dataset_request)
  
        return resp

    @dataset.setter
    async def dataset(self, name: str, size: int, image_type: str, path: str):
        try:
            dataset_request = Dataset(name=name, size=size, type=image_type, url=path)
            resp = await post_async_request_handler(url=f"{base_url}/datasets", request=dataset_request)
        except Exception as ex:
            print(ex)
        
        print('Dataset POST ................Complete')
        return resp

    @property
    async def model(self, name: str) -> Model:
        try:
            model_request = Model(name=name)
            resp = await get_async_request_handler(url=f"{base_url}/models", request=model_request)
        except Exception as ex:
            print(ex)
            pass

        print('Model GET  ................Complete')
        return resp

    @model.setter
    def model(self, name: str, datasets: List[int]):
        try:
            model_request = Model(name=name, datasets=datasets)
            resp = post_async_request_handler(url=f"{base_url}/models", request=model_request)
            print('Model POST  ................Complete')
        except Exception as ex:
            print(ex)
            print('Model POST  ................Failed')
            pass

        return resp
        
    @property
    def image(self) -> Image:
        print('property image called')
        return self._image

    @image.setter
    def image(self, value: Image):
        print('property.setter image called')
        self._image = value

    def extract(self):
        self._extractor.save()

def load_json(file_path: str) -> dict:

    with open(file_path, "rb") as file:
        result = json.load(file)

    return result

if __name__ == "__main__":
    
    loop = get_event_loop()
    
    # Set inputs (UI Service) ##################################################################
    ############################################################################################
    
    human_dataset_base_path = "./ui/dataset_data/human_dataset"
    human_annotations_path = f"{human_dataset_base_path}/annotations/"
    human_images_path = f"{human_dataset_base_path}/images/"

    terminator_dataset_base_path = "./ui/dataset_data/terminator_dataset"
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
    dataset_name = 'terminator_dataset'
    dataset_type = 'jpg'
    dataset_url = human_images_path
    dataset_size = len(list(os.scandir(dataset_url)))
    image_dataset_size = len(glob.glob(human_images_path))
    annotations_dataset_size = len(glob.glob(human_annotations_path))
    
   

    while True:
        try:
           
            image_path = next(terminator_images_path_gen)
            annotations_path = next(terminator_annotations_path_gen)
            if image_dataset_size != annotations_dataset_size:
               raise(
                   (
                       f"Image and annotation folders contain an unequal number of items!"
                       f"Number of images ({image_dataset_size}) != Number of annotations ({annotations_dataset_size})"
                   )
               )
            dataset_type = str(annotations_path).split(".")[-1]
            # dataset_type = 'jpg'
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
            
            image_result = loop.run_until_complete(request_handler_post(url=f"{base_url}/images", request=image_request))
            print('IMAGE POST  ................Complete')
        except StopIteration:
            break
        except Exception as ex:
            print(ex)
            print('IMAGE POST  ................Failed')


    # Now run ML-Extraction (ML-EXTRACT Service) - CPU BOUND, use mulitprocessing, many workers 
    ############################################################################################


    # Save ML outputs internal API format into DB (BACKEND Service) - IO BOUND, use async ######
    ############################################################################################
    
    # print(heatmap)
    # print(bbox_and_categories)
    # print(activations)
    # print(activations_vm.array)