import glob
import os, json
import aiofiles
import aiohttp
import fastapi
from requests import Session
from typing import Generator, List
from asyncio import get_event_loop

from shared.request_handler import request_handler_post
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
    def dataset(self) -> Dataset:
        print('property dataset called')
        return self._dataset

    @dataset.setter
    def dataset(self, value: Dataset):
        print('property.setter dataset called')
        self._dataset = value

    @property
    def model(self) -> Model:
        print('property model called')
        return self._model

    @model.setter
    def model(self, value: Model):
        print('property.setter model called')
        self._model = value

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

async def load_json_async(file_path: str) -> dict:

    async with aiofiles.open(file_path, mode='rb') as f:
        contents = await f.read()

    return contents

async def load_many_json_async(file_path_generator: Generator) -> List[dict]:
    for path in file_path_generator:
        yield await load_json_async(path)

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
    
    try:
        dataset_request = Dataset(name=dataset_name, size=dataset_size, type=dataset_type, url=terminator_dataset_base_path)
        dataset_result = loop.run_until_complete(request_handler_post(url=f"{base_url}/datasets", request=dataset_request))
        print('Dataset POST ................Complete')
    except Exception as ex:
        print(ex)
        print('Dataset POST ................Failed')

    try:
        model_request = Model(name=model_name, datasets=[dataset_name])
        model_result = loop.run_until_complete(request_handler_post(url=f"{base_url}/models", request=model_request))
        print('Model POST  ................Complete')
    except Exception as ex:
        print(ex)
        print('Model POST  ................Failed')
        pass

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
    # print(list_of_images_file_paths_human)
    # heatmap = model.get_img_heatmap(img_path=list_of_images_file_paths_human[0])
    # bbox_and_categories = model.get_model_prediction(img_path=list_of_images_file_paths_human[0])
    # activations = model.get_img_activations(img_path=list_of_images_file_paths_human[0])

    # # Arrange ML outputs into internal API format
    # heatmap_vm = Heatmap(array=heatmap)
    # annotations_vm = Annotations(
    #     bboxes = [BoundingBox(array=bbox) for bbox in bbox_and_categories['bbox']], 
    #     categories = [Category(category_id=cat) for cat in bbox_and_categories['category_id']], 
    # )
    # activations_vm = Activations(array=[activation.tolist() for activation in activations])

    # Save ML outputs internal API format into DB (BACKEND Service) - IO BOUND, use async ######
    ############################################################################################
    
    # print(heatmap)
    # print(bbox_and_categories)
    # print(activations)
    # print(activations_vm.array)