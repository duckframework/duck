"""
Duck view system.

This module defines the base `View` class, which serves as the foundation
for handling HTTP requests in the Duck web framework. Views process incoming
`HttpRequest` objects and return `HttpResponse` objects.

Developers can subclass `View` to define custom request handling logic by
overriding the `run()` method. This abstraction allows separation of business
logic from routing and middleware.
"""
from typing import Optional

from duck.http.request import HttpRequest
from duck.http.response import HttpResponse


class View:
    """
    Base class for Duck views (request handlers).

    A view encapsulates logic to handle an HTTP request and produce a response.
    Views are instantiated per request and can carry state during request processing.

    Subclasses should override the `run()` method to implement custom behavior.

    Attributes:
        request (HttpRequest): The incoming HTTP request object.
        kwargs (dict): Additional parameters extracted from the route (e.g., path variables).
    """

    def __init__(self, request: HttpRequest, **kwargs):
        """
        Initializes the view with the incoming request and any route parameters.

        Args:
            request (HttpRequest): The HTTP request to be handled.
            **kwargs: Arbitrary keyword arguments passed from the URL routing, such as path variables.
        """
        self.request = request
        self.kwargs = kwargs

    def strictly_async(self) -> bool:
        """
        Indicates whether the view requires asynchronous execution.

        This is useful in environments like WSGI, where strictly asynchronous
        views should be deferred to an async execution queue instead of being
        executed synchronously.

        Override this method if your view contains non-blocking I/O or requires
        an event loop context.

        Returns:
            bool: True if the view should be treated as strictly async, False otherwise.
        """
        return False

    def run(self) -> Optional[HttpResponse]:
        """
        Handles the request and returns an HTTP response.

        This method should be overridden by subclasses to implement
        custom request handling logic. It must return an `HttpResponse`
        object to be sent to the client.

        If no response is expected (e.g., in cases of low-level socket handling),
        raise `duck.exceptions.all.ExpectingNoResponse` and handle the response
        manually using `request.client_socket` and `request.client_address`.

        Returns:
            Optional[HttpResponse]: The HTTP response or data that can be converted to HTTP response to be returned to the client.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the run() method and return the appropriate response.")
