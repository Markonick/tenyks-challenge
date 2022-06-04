import asyncio
from dataclasses import dataclass
import glob
import os, json
from abc import ABC, abstractmethod
import time
import aiofiles

from app.shared.view_models import Dataset, Image, Model
from model_data import DummyModel

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

async def load_many_json_async(files_list):
     return await asyncio.gather(
            *(load_json_async(file) for file in files_list)
        )

# @dataclass
# class 
if __name__ == "__main__":
    # json_extractor: BaseExtractor = JsonExtractor(input)
    # tenyks_sdk = TenyksSDK(json_extractor)
    
    loop = asyncio.get_event_loop()
    # tenyks_sdk.extract(json_extractor)
    # annotations_path = "/Users/nicolas/Projects/tenyks-challenge/dataset_data/human_dataset/annotations/"
    annotations_path = "/Users/nicolas/Projects/tenyks-challenge/annotations/"
    images_path = "/Users/nicolas/Projects/tenyks-challenge/dataset_data/human_dataset/images/"
    list_of_annotations_file_paths = glob.glob(f"{annotations_path}*.json")
    list_of_images_file_paths = glob.glob(f"{images_path}*.jpg")
    # print(list_of_annotations_file_paths)
    print(f"start blocking_io at {time.strftime('%X')}")
    result = [load_json(file) for file in list_of_annotations_file_paths]
    print(f"finish blocking_io at {time.strftime('%X')}")
    # result2 = 
    # print(result)
    # print(result2)
    print(glob.glob("*.jpg"))
    print(f"start async read at {time.strftime('%X')}")
    loop.run_until_complete(load_many_json_async(list_of_annotations_file_paths))
    print(f"finish async read at {time.strftime('%X')}")
    loop.close()
    model_id = 0
    model = DummyModel(model_id)
    heatmap = model.get_img_heatmap(img_path=list_of_images_file_paths[0])
    bbox_and_categories = model.get_model_prediction(img_path=list_of_images_file_paths[0])
    activations = model.get_img_activations(img_path=list_of_images_file_paths[0])
    print(heatmap)
    print(bbox_and_categories)
    print(activations)
