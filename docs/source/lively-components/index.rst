Lively / HTML Components
=========================

The Duck Framework **Lively Component System** lets you build reactive,
real-time web UIs entirely in Python — no JavaScript required for most
interactions. It uses WebSockets with msgpack to sync component state
between the browser and the server, and supports fast, partial-reload
navigation between pages.

Example:

.. code-block:: python

   from duck.html.components.page import Page
   from duck.html.components.button import Button

   class HomePage(Page):
       def on_create(self):
           super().on_create()
           self.add_to_body(Button(text="Hello world"))

Use the following pages to learn about each part of the system.

.. toctree::
   :maxdepth: 1

   01-lively-overview-and-page-basics
   02-lively-events-forms-file-uploads
   03-lively-advanced-rendering-and-reference
