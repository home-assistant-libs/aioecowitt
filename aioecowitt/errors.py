"""Define package errors."""


class EcoWittError(Exception):
    """Define a base error."""


class RequestError(EcoWittError):
    """Define an error related to invalid requests."""