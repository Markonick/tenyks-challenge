from abc import ABC, abstractmethod
import json
from typing import Callable, List
from asyncpg.connection import Connection
import pydantic
import numpy as np

from shared.encoders import NumpyEncoder
from shared.types_common import ExtractionTypes
from shared.view_models import Activations, Annotations, Heatmap
from shared.model_data import DummyModel


class ExtractionTypeBase(ABC):

    @abstractmethod
    def run(self, img_path: str):
        pass


class HeatmapExtraction(ExtractionTypeBase):
    def __init__(self, model_id):
        self._model = DummyModel(model_id)

    def run(self, img_path: str) -> Heatmap: 
        """Get heatmap  for an image based on model id"""
           
        heatmap = self._model.get_img_heatmap(img_path=img_path)
        return Heatmap(array=json.dumps(heatmap, cls=NumpyEncoder))


class ActivationsExtraction(ExtractionTypeBase):
    def __init__(self, model_id):
        self._model = DummyModel(model_id)

    def run(self, img_path: str) -> Activations:
        """Get activations for an image based on model id"""
 
        activations = self._model.get_img_activations(img_path=img_path)
        return Activations(array=json.dumps(activations, cls=NumpyEncoder))


class PredictionsExtraction(ExtractionTypeBase):
    def __init__(self, model_id):
        self._model = DummyModel(model_id)

    def run(self, img_path: str) -> Annotations:
        """Get bounding boxes and their respective categories for an image based on model id"""

        bbox_and_categories = self._model.get_model_prediction(img_path=img_path)
        return bbox_and_categories

def dispatch_extractor_service(model_id: int, extraction_type: ExtractionTypes, img_path: str):
    return {
        ExtractionTypes.HEATMAP: lambda: HeatmapExtraction(model_id=model_id).run(img_path),
        ExtractionTypes.ACTIVATIONS: lambda: ActivationsExtraction(model_id=model_id).run(img_path),
        ExtractionTypes.PREDICTIONS: lambda: PredictionsExtraction(model_id=model_id).run(img_path),
    }.get(extraction_type, lambda: None)()