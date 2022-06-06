import logging
from typing import Union
from fastapi.exceptions import RequestValidationError

from .types_common import StatusGroup

logger = logging.getLogger(__name__)


class TenyksException(Exception):
    def __init__(self, ex: str):
        self._ex = ex

class TenyksRequestValidationError(RequestValidationError):
    def __init__(self, ex: str):
        self._ex = ex