from itertools import tee
from mailbox import Babyl
import os, json
from abc import ABC, abstractmethod

"""
A client should be able to use the Tenyks SDK in order to perform the following actions:
- Save
- Load
- Extract

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
        self._extractor = extractor
    
    def save_dataset(self):
        pass

    def save_model(self):
        pass

    def save_image(self):
        pass

    def get_dataset(self):
        pass

    def get_model(self):
        pass

    def get_image(self):
        pass

    def extract(self):
        self._extractor.save()

if __name__ == "__main__":
    json_extractor: BaseExtractor = JsonExtractor(input)
    tenyks_sdk = TenyksSDK(json_extractor)

    tenyks_sdk.extract(json_extractor)
