"""
Module containing Duck error classes.
"""


class BaseException(Exception):
    """
    Base class for all errors.
    """
    
    def __init__(self, message, **kws):
        """
        Stores the error message in the `message` attribute.

        Args:
            message (str): The error message.
            **kws: Additional keyword arguments.
        """
        self.message = message

    def __str__(self):
        """
        Returns the error message.
        """
        return f"{self.message}"


class AsyncViolationError(BaseException):
   """
   Raised on operations which violates asynchronous way of doing things.
   """


class ExpectingNoResponse(BaseException):
    """
    Exception raised when we are expecting a response yet we are never going to
    get any. Useful in cases where methods like `get_response` are expecting a response e.g. from
    a WebSocketView yet this view handles everything on its own and no response is supposed to be returned.
    """


class DisallowedAction(BaseException):
    """
    Raised on disallowed actions.
    """

    
class ServerError(BaseException):
    """
    Server based exceptions.
    """


class ApplicationError(BaseException):
    """
    Raised on application related errors.
    """


class BlueprintError(BaseException):
    """
    Raised for blueprint-related errors.
    """


class PortError(BaseException):
    """
    Raised on port conflict errors.
    """


class RequestError(BaseException):
    """
    Raised for request errors.
    """


class RequestHostError(RequestError):
    """
    Raised on request host errors.
    """


class MethodNotAllowedError(RequestError):
    """
    Raised on disallowed request method.
    """


class RequestSyntaxError(RequestError):
    """
    Raised on request syntax errors.
    """


class RequestUnsupportedVersionError(RequestError):
    """
    Raised on unsupported HTTP version.
    """


class RequestTimeoutError(RequestError):
    """
    Raised on request timeouts.
    """


class HeaderError(BaseException):
    """
    Raised on header-related exceptions.
    """


class RouteError(BaseException):
    """
    Raised on errors related to routes and route configuration.
    """


class RouteNotFoundError(BaseException):
    """
    Raised on unregistered or unknown routes.
    """


class FunctionError(BaseException):
    """
    Raised on function errors.
    """


class CustomHeadersJsonLoadError(BaseException):
    """
    Raised when there's an error loading custom headers from JSON.
    """


class MiddlewareError(ApplicationError):
    """
    Raised when there's an error on any middleware.
    """


class MiddlewareLoadError(MiddlewareError):
    """
    Raised when there's an error loading or importing a middleware.
    """


class NormalizerError(BaseException):
    """
    Raised when there's an error on any normalizer.
    """


class NormalizerLoadError(NormalizerError):
    """
    Raised when there's an error loading or importing a normalizer.
    """


class CSRFMiddlewareError(MiddlewareError):
    """
    Raised when there's an error in CSRF middleware.
    """


class NormalizationError(BaseException):
    """
    Raised when there's an error in normalization process.
    """


class SettingsError(BaseException):
    """
    Raised for errors in the app's settings configuration.
    """


class ContentError(BaseException):
    """
    Raised for error related to setting content of an HttpResponse.
    """


class TemplateError(BaseException):
    """
    Raised for any errors related to templates.
    """


class TemplateNotFound(TemplateError):
    """
    Raised when a template could not be found.
    """


class SSLError(BaseException):
    """
    Raised when ssl certfile or ssl private key is not found in locations specified in settings.py if and only if
    `ENABLE_HTTPS=True`
    """


class MultiPartParserError(BaseException):
    """
    Exception when parsing multipart/form-data
    """
