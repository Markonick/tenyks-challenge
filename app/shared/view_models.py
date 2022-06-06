from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from dataclasses import dataclass as non_pyd_dataclass
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

@non_pyd_dataclass
class Heatmap:
    """Representation of a Heatmap"""

    array: np.ndarray = field(default_factory=lambda: np.zeros(10))

@non_pyd_dataclass
class Activations:
    """Representation of a Layer Activations"""

    array: List[np.ndarray] = field(default_factory=lambda: np.zeros(10))

# class Activations(BaseModel):
#     array: np.ndarray = Field(default_factory=lambda: np.zeros(10))

#     class Config:
#         arbitrary_types_allowed = True

@non_pyd_dataclass
class Image:
    """Information about each image"""
    
    name: str
    annotations: Annotations
    model_annotations: Optional[Annotations] = Field(default_factory=lambda: np.zeros(10))
    model_heatmap: Optional[Heatmap] = None
    model_activations: Optional[Activations] = Field(default_factory=lambda: np.zeros(10))

