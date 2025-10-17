from duck.http.middlewares.contrib.session import SessionMiddleware
from duck.http.middlewares.contrib.django import DjangoRequestFixerMiddleware
from duck.http.middlewares.contrib.www_redirect import WWWRedirectMiddleware

__all__ = [
    'SessionMiddleware',
    'DjangoRequestFixerMiddleware',
    'WWWRedirectMiddleware',
]
