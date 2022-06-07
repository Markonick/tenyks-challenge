from abc import ABC, abstractmethod
import json
from typing import Callable, List
from asyncpg.connection import Connection
import pydantic
import numpy as np

from shared.view_models import Annotations
from shared.model_data import DummyModel


class ExtractionTypeBase(ABC):
    def __init__(self, model_id):
        self._model = DummyModel(model_id)

    @abstractmethod
    def run(self, img_path: str):
        pass


class HeatmapExtraction(ExtractionTypeBase):
    def run(self, img_path: str) -> np.ndarray: 
        """Get heatmap  for an image based on model id"""
           
        heatmap = self._model.get_img_heatmap(img_path=img_path)
        return heatmap


class ActivationsExtraction(ExtractionTypeBase):
    def run(self, img_path: str) -> List[np.ndarray]:
        """Get activations for an image based on model id"""
 
        activations = self._model.get_img_activations(img_path=img_path)
        return activations


class PredictionsExtraction(ExtractionTypeBase):
    def run(self, img_path: str) -> Annotations:
        """Get bounding boxes and their respective categories for an image based on model id"""

        bbox_and_categories = self._model.get_model_prediction(img_path=img_path)
        return bbox_and_categories


class ExtractionService:
    """Service responsible for extracting """

    def __init__(self, extraction_types: List[Callable]) -> None:
        self._extraction_types = extraction_types
        
    def get_img_heatmap(self, img_path: str) -> np.ndarray:
        """Get heatmap  for an image based on model id"""
        
        heatmap = self._model.get_img_heatmap(img_path=img_path)
        return heatmap

    def get_model_prediction(self, img_path: str) -> Annotations:
        """Get bounding boxes and their respective categories for an image based on model id"""

        bbox_and_categories = self._model.get_model_prediction(img_path=img_path)
        return bbox_and_categories

    def get_img_activations(self, img_path: str) -> List[np.ndarray]:
        """Get activations for an image based on model id"""

        activations = self._model.get_img_activations(img_path=img_path)
        return activations