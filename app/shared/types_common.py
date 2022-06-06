from pydantic.dataclasses import dataclass
from enum import Enum, unique
from typing import Generic, Type, TypeVar, Union
from pydantic.generics import GenericModel

RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")


@unique
class StatusGroup(str, Enum):
    SUCCESS = "success"
    CLIENT_ERROR = "client_error"
    INTERNAL_ERROR = "internal_error"
    TEMPORARY_ERROR = "temporary_error"


class TenyksSuccess(GenericModel, Generic[ResponseT]):
    result: ResponseT
    type: StatusGroup = StatusGroup.SUCCESS


@dataclass
class TenyksError:
    message: str
    type: StatusGroup = StatusGroup.INTERNAL_ERROR
    

class TenyksResponse(GenericModel, Generic[ResponseT]):
    response: Union[TenyksSuccess[ResponseT], TenyksError]


