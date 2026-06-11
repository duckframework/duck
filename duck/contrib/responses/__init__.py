"""
Duck Framework built-in response factory.

Transforms bare HttpResponse subclasses into fully rendered,
themed HTML responses using Duck's internal template engine.

"""
from duck.contrib.responses.base import make_response, async_make_response

__all__ = ["make_response", "async_make_response"]
