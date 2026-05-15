from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse


class FastShipException(Exception):
    """Base class for all exceptions in fastship API"""

    def __init__(self, *args: object, detail: str | None = None) -> None:
        super().__init__(*args)
        self.detail = detail or self.__class__.__doc__

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class EnitityNotFoundException(FastShipException):
    """The object does not exists"""

    status_code = status.HTTP_404_NOT_FOUND


class InvalidTokenException(FastShipException):
    """Invalid or expired Token"""

    status_code = status.HTTP_401_UNAUTHORIZED


class EmailNotVerifiedException(FastShipException):
    """Email not verified"""

    status_code = status.HTTP_401_UNAUTHORIZED


class DeliveryPartnerNotAvailableException(FastShipException):
    "No delivery partner available"

    status_code = status.HTTP_406_NOT_ACCEPTABLE


class ShipmentUpdateEmptyException(FastShipException):
    """No shipment update provided"""

    status_code = status.HTTP_406_NOT_ACCEPTABLE


class InvalidVerificationCodeException(FastShipException):
    """Invalid verification code provided"""

    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidTagException(FastShipException):
    """Provided tag is invalid"""

    status_code = status.HTTP_400_BAD_REQUEST


class TagAlreadyAssignedError(FastShipException):
    """Tag already assigned to the shipment"""

    status_code = status.HTTP_400_BAD_REQUEST


class TagNotAssignedError(FastShipException):
    """Provided tag is not assigned to the shipment"""

    status_code = status.HTTP_400_BAD_REQUEST


def exception_handler(request: Request, exception: FastShipException) -> Response:
    return JSONResponse(
        status_code=exception.status_code, content={"details": exception.detail}
    )


def response_validation_error_handler(
    request: Request, exception: ResponseValidationError
):
    return JSONResponse(
        content="Something went wrong..",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def add_exception_handlers(app: FastAPI):
    for subclass in FastShipException.__subclasses__():
        app.add_exception_handler(subclass, exception_handler)

    # app.add_exception_handler(ResponseValidationError, response_validation_error_handler)
