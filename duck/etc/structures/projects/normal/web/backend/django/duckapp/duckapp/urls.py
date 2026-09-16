"""
Django URL Patterns Registration Module

This module is utilized by Django to register URL patterns using the Duck framework.

WARNING: Do not overwrite the `urlpatterns` variable as it contains all URL patterns registered using Duck.

Instead of overwriting `urlpatterns`, append your new URL patterns to the list.

"""
from django.contrib import admin

from django.urls import path, re_path, include
from duck.backend.django import urls as duck_urls

urlpatterns = duck_urls.urlpatterns + [
    path('admin/', admin.site.urls),
    # Your new URL patterns here...
]
