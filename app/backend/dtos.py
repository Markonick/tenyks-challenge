from pydantic.dataclasses import dataclass
from typing import List, Optional

from shared.view_models import BoundingBox, Category


@dataclass
class DatasetDto:
    """DTO used to represent a dataset row"""

    id: int
    dataset_type_id: int
    dataset_name: str
    dataset_size: int
    dataset_url: str
    images_url: str

@dataclass
class ModelDto:
    """DTO used to represent a dataset row"""

    id: int
    name: str
    dataset_type_id: int            
    dataset_name: str
    dataset_size: int
    dataset_url: str
    images_url: str
    
@dataclass
class ImageDto:
    """DTO used to represent a dataset row"""

    id: int
    name: str
    dataset_id: int
    bboxes: List[BoundingBox]
    categories: List[Category]
    images_url: str
    dataset_name: str