from pydantic.dataclasses import dataclass
from enum import Enum, unique
from typing import Generic, Optional, Type, TypeVar, Union
from pydantic.generics import GenericModel
from fastapi import Request

from shared.view_models import Annotations

RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


@unique
class ImageSearchFilter(str, Enum):
    ALL = "all"
    SINGLE = "single"

@unique
class StatusGroup(str, Enum):
    SUCCESS = "success"
    CLIENT_ERROR = "client_error"
    INTERNAL_ERROR = "internal_error"
    TEMPORARY_ERROR = "temporary_error"

@unique
class ExtractionTypes(str, Enum):
    HEATMAP = "heatmap"
    ACTIVATIONS = "activations"
    PREDICTIONS = "predictions"

class TenyksSuccess(GenericModel, Generic[ResponseT]):
    result: ResponseT
    type: StatusGroup = StatusGroup.SUCCESS

@dataclass
class TenyksError:
    message: str
    type: StatusGroup = StatusGroup.INTERNAL_ERROR
    
@dataclass
class TenyksExtractionRequest:
    dataset_name: str
    model_name: str
    type: ExtractionTypes
    image_search_filter: Optional[ImageSearchFilter] = ImageSearchFilter.ALL 
    image_name: Optional[str] = None
    
@dataclass
class TenyksDatasetsRequest:
    dataset_name: str

@dataclass
class TenyksModelsRequest:
    model_name: str
   
@dataclass 
class TenyksImagesRequest:
    dataset_name: str
    image_name: Optional[str] = None

@dataclass 
class TenyksModelImagesRequest:
    image_id: int
    model_name: str
    dataset_name: str
    extraction_type: ExtractionTypes
    result_path: Optional[str] = None
    model_annotations: Optional[Annotations] = None


class TenyksResponse(GenericModel, Generic[ResponseT]):
    response: Union[TenyksSuccess[ResponseT], TenyksError]


