from typing import Any, List, Optional
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from dataclasses import dataclass as non_pydantic_dataclass
from dataclasses import field
import numpy as np


@dataclass
class Dataset:
    """Information about each dataset as a whole"""
    
    Key = int

    name: str
    size: int
    type: str
    url: str

@dataclass
class Model:
    """Information about each model as a whole"""

    Key = int

    name: str
    datasets: List[str]
    
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

    bboxes: List[BoundingBox]
    categories: List[Category]

@dataclass
class Heatmap:
    """Representation of a Heatmap"""

    # array: np.ndarray = field(default_factory=lambda: np.zeros(10))
    array: Any

@dataclass
class Activations:
    """Representation of a Layer Activations"""

    # array: List[np.ndarray] = field(default_factory=lambda: List[np.zeros(10)])
    array: List[Any]

@dataclass
class Image:
    """Information about each image"""
    
    name: str
    url: str
    dataset_name: str
    annotations: Annotations
    model_annotations: Optional[Annotations] = None
    model_activations: Optional[Activations] = None
    model_heatmap: Optional[Heatmap] = None

