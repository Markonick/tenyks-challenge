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
    dataset_path: str
    images_path: str

@dataclass
class ModelDto:
    """DTO used to represent a dataset row"""

    id: int
    name: str
    datasets: List[str]
    
@dataclass
class ImageDto:
    """DTO used to represent a dataset row"""

    id: int
    name: str
    dataset_id: int
    bboxes: List[BoundingBox]
    categories: List[Category]
    images_path: str
    dataset_name: str
    model_bboxes: Optional[List[BoundingBox]] = None
    model_categories: Optional[List[Category]] = None
    model_heatmap: Optional[str] = None
    model_activations: Optional[str] = None