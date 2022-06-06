import os, json
import asyncio
from dataclasses import dataclass
import glob
from abc import ABC, abstractmethod
import time
import aiofiles
import requests
from typing import Generator, List

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
class BaseExtractor(ABC):
    def __init__(self, input,):
        self._input = input

    @abstractmethod
    def save(self, input):
        pass

class JsonExtractor(BaseExtractor): 
    def __init__(self, input: json) -> None:
        super().__init__(input)

class TenyksSDK():
    def __init__(self, extractor: BaseExtractor) -> None:
        self._dataset = ""
        self._model = ""
        self._image = ""
        self._extractor = extractor

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

# def ml_extraction()
def load_json(file_path: str) -> dict:

    with open(file_path,'r') as file:
        result = json.load(file)

    return result

async def load_json_async(file_path: str) -> dict:

    async with aiofiles.open(file_path, mode='r') as f:
        contents = await f.read()

    return contents

async def load_many_json_async(file_path_generator: Generator) -> List[dict]:
    for path in file_path_generator:
        yield await load_json_async(path)

if __name__ == "__main__":
    # json_extractor: BaseExtractor = JsonExtractor(input)
    # tenyks_sdk = TenyksSDK(json_extractor)
    
    loop = asyncio.get_event_loop()
    # tenyks_sdk.extract(json_extractor)
    
    # Set inputs (UI Service) ##################################################################
    ############################################################################################
    # annotations_path = "/Users/nicolas/Projects/tenyks-challenge/dataset_data/human_dataset/annotations/"
    dataset_path_human = "./ui/dataset_data/human_dataset"
    dataset_path_terminator = "./ui/dataset_data/terminator_dataset"
    annotations_path_human = f"{dataset_path_human}/annotations/"
    annotations_path_terminator = f"{dataset_path_terminator}/annotations/"
    images_path_human = f"{dataset_path_human}/images/"
    images_path_terminator = f"{dataset_path_terminator}/images/"
    list_of_annotations_file_paths_human = glob.glob(f"{annotations_path_human}*.json")
    list_of_annotations_file_paths_terminator = glob.glob(f"{images_path_terminator}*.json")
    list_of_images_file_paths_human = glob.glob(f"{images_path_human}*.jpg")
    list_of_images_file_paths_terminator = glob.glob(f"{images_path_terminator}*.jpg")

    list_of_images_file_paths_terminator =os.scandir(images_path_terminator)
    print(type(os.walk(images_path_terminator)))
    print(type(os.walk(images_path_terminator)))
    print(type(os.walk(images_path_terminator)))
    print(type(os.walk(images_path_terminator)))
    print(type(os.walk(images_path_terminator)))
    print(type(os.walk(images_path_terminator)))

    # Read Json annotations files (UI Service) - IO BOUND, use async ###########################
    ############################################################################################
    print(f"start blocking_io at {time.strftime('%X')}")
    result = [load_json(file) for file in list_of_annotations_file_paths_human]
    print(f"finish blocking_io at {time.strftime('%X')}")

    # Async Read Json annotations files (UI Service) - IO BOUND, use async #####################
    ############################################################################################
    # print(f"start async read at {time.strftime('%X')}")
    # loop.run_until_complete(load_many_json_async(list_of_annotations_file_paths_human))os.walk(images_path_terminator)
    # print(f"finish async read at {time.strftime('%X')}")
    # loop.close()

    # First prepare data #######################################################################
    ############################################################################################
    size_human = len(list_of_annotations_file_paths_human)
    size_terminator = len(list_of_annotations_file_paths_human)
    model_id = 0
    dataset_name_human = "human_dataset"
    dataset_name_terminator = "terminator_dataset"
    model_name = "Terminator Model"
    dataset_human_vm = Dataset(name=dataset_name_human, size=size_human, type='jpg', url=dataset_path_human)
    dataset_terminator_vm = Dataset(name=dataset_name_terminator, size=size_terminator, type='jpg', url=images_path_terminator)
    model_vm = Model( name=model_name, datasets=[dataset_human_vm.name, dataset_terminator_vm.name])
    
    # Persist dataset data into DB (BACKEND Service) - IO BOUND, use async #####################
    ############################################################################################
    backend_url = "http://backend:8000/api/datasets"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data={
        "type": "jpg",
        "name": "terminator_dataset5",
        "size": 12,
        "url": "here/is/the/path4"
    }

    files_generator = os.walk(images_path_terminator)
    # loop.run_until_complete(load_many_json_async(path_generator))
    with requests.Session() as session:
        for dirpath, dirname, filename in files_generator:
            print(dirpath)
            print(dirname)
            print(filename)
            data = loop.run_until_complete(load_json_async(dirpath))

            session.post(backend_url, headers=headers, json=data)
    
    # Now run ML-Extraction (ML-EXTRACT Service) - CPU BOUND, use mulitprocessing, many workers 
    ############################################################################################
    
    model = DummyModel(model_id)
    # print(list_of_images_file_paths_human)
    heatmap = model.get_img_heatmap(img_path=list_of_images_file_paths_human[0])
    bbox_and_categories = model.get_model_prediction(img_path=list_of_images_file_paths_human[0])
    activations = model.get_img_activations(img_path=list_of_images_file_paths_human[0])

    # Arrange ML outputs into internal API format
    heatmap_vm = Heatmap(array=heatmap)
    annotations_vm = Annotations(
        bboxes = [BoundingBox(array=bbox) for bbox in bbox_and_categories['bbox']], 
        categories = [Category(category_id=cat) for cat in bbox_and_categories['category_id']], 
    )
    activations_vm = Activations(array=[activation.tolist() for activation in activations])

    # Save ML outputs internal API format into DB (BACKEND Service) - IO BOUND, use async ######
    ############################################################################################
    
    # print(heatmap)
    # print(bbox_and_categories)
    # print(activations)
    # print(activations_vm.array)