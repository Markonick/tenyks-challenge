from typing import List
from dataclasses import dataclass
import numpy as np


@dataclass
class Dataset:
    """Information about each dataset as a whole"""

    name: str
    size: int
    type: str
    url: str

@dataclass
class Model:
    """Information about each model as a whole"""
    Key = int
    model_id: int
    name: str
    datasets: List[Dataset]
    
@dataclass
class BoundingBox:
    """Information about image bounding box"""

    array: List[int]

@dataclass
class Category:
    """Bounding box Category"""

    category_id: int

@dataclass
class Annotations:
    """Representation of annotations"""

    bbox: List[BoundingBox]
    category: List[Category]

@dataclass
class Heatmap:
    """Representation of a Heatmap"""

    array: np.ndarray

@dataclass
class Activations:
    """Representation of a Layer Activations"""

    array: List[np.ndarray]

@dataclass
class Image:
    """Information about each image"""
    
    name: str
    annotations: Annotations
    model_annotations: Annotations
    model_heatmap: Heatmap
    model_activations: Activations

