from pydantic.dataclasses import dataclass
from enum import Enum, unique
from typing import Generic, Type, TypeVar, Union
from pydantic.generics import GenericModel
from fastapi import Request

RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


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
    
@dataclass
class TenyksDatasetsRequest:
    dataset_name: str

@dataclass
class TenyksModelsRequest:
    model_name: str
   
@dataclass 
class TenyksImagesRequest:
    dataset_name: str
@dataclass 

class TenyksModelImagesRequest:
    dataset_name: str
    heatmap_path: str
    activations_path: str

class TenyksResponse(GenericModel, Generic[ResponseT]):
    response: Union[TenyksSuccess[ResponseT], TenyksError]


