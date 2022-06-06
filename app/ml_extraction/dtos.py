from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class DatasetDto:
    """DTO used to represent a dataset row"""

    id: int
    dataset_type_id: int
    dataset_name: str
    dataset_size: int
    dataset_url: str

@dataclass
class ModelDto:
    """DTO used to represent a dataset row"""

    id: int
    name: str
    
@dataclass
class ImageDto:
    """DTO used to represent a dataset row"""

    id: int
    bbox_id: int
    category_id: int