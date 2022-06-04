import os, json
from abc import ABC, abstractmethod

from app.shared.view_models import Dataset, Image, Model

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

def load_json(file_path: str) -> dict:
    with open(file_path,'r') as file:
        return json.load(file)

if __name__ == "__main__":
    json_extractor: BaseExtractor = JsonExtractor(input)
    tenyks_sdk = TenyksSDK(json_extractor)

    tenyks_sdk.extract(json_extractor)

    image_path = "../dataset_data/human_dataset/annotations/11.json"
    result = load_json(image_path)
    print(result)