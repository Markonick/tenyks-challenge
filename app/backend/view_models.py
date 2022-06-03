from typing import List
from dataclasses import dataclass
import numpy as np

@dataclass
class Dataset:
    """Information about each dataset as a whole"""
    name: str
    size: int
    type: str

@dataclass
class Model:
    """Information about each model as a whole"""
    model_id: int
    name: str
    datasets: List[Dataset]
    
@dataclass
class Image:
    """Information about each image"""
    name: str
    bbox: List[List[int]]
    category: List[int]
    model_bbox: List[List[int]]
    model_category: List[int]
    model_heatmap: np.ndarray
    model_activations: List[np.ndarray]

