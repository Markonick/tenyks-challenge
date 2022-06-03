from typing import Union
from pickle import DICT
from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from shared.types_common import (
    ComponentError,
    ComponentResponse,
    JobId,
    StatusGroup,
)
import logging

logger = logging.getLogger(__name__)


def _get_content_for_exception(
    exc: Exception, msg: dict, status_group: StatusGroup
) -> Union[dict, ComponentResponse]:
    """
    Tries to compose a response body wrapped in Mia Envelope,
    if the Exception.body is present and JobId is present in the Request
    """
    try:
        jobId = JobId(**exc.body["jobId"])
        content = ComponentResponse(
            jobId=jobId,
            response=ComponentError(
                type=status_group,
                message=msg,
            ),
        ).dict()
    except Exception as e:
        logger.error(e)
        content = msg

    return content


async def exception_handler(request: Request, exc: Exception):
    msg = str(exc)
    content = _get_content_for_exception(exc, msg, StatusGroup.INTERNAL_ERROR)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(content),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    msg = str(exc.errors())
    content = _get_content_for_exception(exc, msg, StatusGroup.CLIENT_ERROR)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(content),
    )


def create_app() -> FastAPI:
    """
    Create a FastAPI instance with custom exception handlers
    """
    app = FastAPI()

    # app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # app.add_exception_handler(Exception, exception_handler)

    return app
