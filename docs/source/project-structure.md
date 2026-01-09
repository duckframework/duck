# 🌀 Project structure

The following includes **Duck** full project structure.

## Full project structure

```bash
myproject/ # Root Project
├── assets/ # Some project assets, logs, etc.
├── etc/ # Configuration files directory
│     ├── ssl/
│     │       ├── server.crt # Default Duck server certificate
│     │       └── server.key # Default Duck server private key
│     └── README.md # Duck etc readme file
├── web/ # Directory containing most python scripts
│       ├── backend/  
│       │   └── django/  
│       │       ├── duckapp/  # Default Django project
│       │       │   ├── duckapp/ # Default Django root applicatiob
│       │       │   │    ├── urls.py  # Django URL config (edited by Duck)
│       │       │   │    ├── views.py  # Django views configuration
│       │       │   │    ├── settings.py # Django settings config (edited by Duck)
│       │       │   │    └── ...  
│       │       │   └── manage.py # Django management file
│       │       └── ...
│       ├── ui/  #  Directory for the frontend e.g., components, pages, templates & staticfiles
│       │       ├── components/  # Directory for storing reusable Lively components
│       │       ├── pages # Structured Lively page components
│       │       ├── static # Static files for the app.
│       │       ├── templates # Application templates
│       │       └── ...
│       ├── automations.py # Your Duck automations 
│       ├── main.py # Duck main app execution file
│       ├── settings.py # Duck settings configuration
│       ├── urls.py # Duck URL configuration
│       ├── views.py # Your request handling views
│       └── templatetags.py # Your custom template tags and filters   
│
├── .env # Your environment variables file
├── .gitignore # Your Gitignore file (useful for Git)
├── requirements.txt # Requirements/dependancies for your project
├── LICENSE # Your License file
├── README.md # Your project Readme
└── TODO.md # Your Todo file

```

``` {note}
From the above project structure, this includes the files and directories of the full project version but for the other
project versions, some files or directories will be ommitted.
```

---


## Application Files

### main.py

This is the main entry point or primary Python file for running a **Duck** project. It can also serve as an alternative to the `duck runserver` command, allowing you to start your application directly.

```py

from duck.app import App

# Initialize the app with a specified port and address
# Use App(port=8000, addr='::1', uses_ipv6=True) for IPv6 support
app = App(port=8000, addr='127.0.0.1')  

if __name__ == '__main__':
    # Start the application when the script is executed directly
    app.run()
```

#### Explanation:

- **App Object:** This object initializes the application with a specified port (8000) and address (127.0.0.1), which corresponds to localhost. You can easily modify these values to fit your needs. For instance, you can change the port or use IPv6 by setting `addr='::1'` and `uses_ipv6=True`.  
- **app.run():** This method starts the application, allowing it to listen for incoming HTTP requests at the specified address and port. It keeps the server running and responsive to client interactions.
- **if __name__ == "__main__":** This conditional check ensures that the `app.run()` method is only invoked when the script is executed directly. It prevents the app from running if the file is imported as a module into another script.

### settings.py

This is the central configuration file for all Duck project settings, where you can manage various application-wide settings in one place. It simplifies the process of configuring the behavior of your app across different environments and use cases.

### views.py

This file contains the logic for generating content that will be displayed on various URL endpoints of your application. Each view is linked to a specific URL endpoint and is responsible for returning content when a user accesses that endpoint.

For example, the `/home` endpoint might display a simple message, `Hello world`. In this case, the view responsible for this would return a heading like `<h1>Hello world</h1>`. Views can be functions, methods, or any callable objects that return content for preview.

``` {important}
Every view expects a `request` argument to be passed to it. The `request` represents the user's HTTP request (sent when accessing the browser). The `request` object provides context and data about the user's request, which allows you to dynamically generate responses based on the request. For instance, you could check whether the user is logged in and display different content accordingly.

You can explore the `duck.http.response` module for various types of responses you can send to users. This module includes functionality for handling different data formats, such as plain text, HTML, video, images, and other file types. By using the responses available in this module, you can effectively manage the content you return to users based on their requests.
```

```py
from duck.views import View


def home(request):
    # Some function-based view
    return "<h1>Hello world</h1>" # or a duck.http.HttpResponse object.


async def async_home(request):
    # Some asynchronous function-based view
    return "<h1>Hello world</h1>" # or a duck.http.HttpResponse object.


class SomeView(View):
    # Some class-based view
    def run(self):
        return "<h1>Hello world</h1>"


class SomeAsyncView(View):
    # Some asynchronous class-based view
    async def run(self):
        return "<h1>Hello world</h1>"

```

---

### urls.py

The `urls.py` file serves as the backbone for mapping URL endpoints to their corresponding views in the application. It defines how incoming requests to various URLs are routed to specific views for processing.

In the example below, we link the root URL endpoint `/` to a view called `home`, which is defined in the `views.py` module. The `urls.py` file manages this mapping through a variable called `urlpatterns`, which is a list containing the URL patterns and their associated views.

Each entry in `urlpatterns` consists of:
- **Route**: The URL path or endpoint.
- **View**: The view function or callable that handles the request for that route.
- **Name**: An optional name for the endpoint, allowing you to reference it dynamically.
- **Methods**: List of methods to supported for the provided endpoint.

Here’s a simple example of how **URL routing** works in `urls.py`:

```py

from duck.urls import path, re_path
from some_module import views # import your views module here

urlpatterns = [  
    path("/", views.home, "home", methods=["GET"]), # methods argument is optional
    # You can also use re_path/regex path here
]

```

```{note}
The following section is optional. You may skip to the next chapter if you prefer not to dive into the details of `urls.py`.
```

---

### urls.py in Detail

As previously mentioned, `urlpatterns` is a list that contains the mappings of different URL endpoints to their corresponding views. This list is the core of the URL routing system.

The `urlpatterns` list expects each entry to be a `URLPattern` object, which can be easily created using the two functions `path` and `re_path` from the `duck.urls` module.

These functions accept the following arguments:
- **route**: The URL endpoint that the function will match.
- **view**: The view function that will handle the request for this URL.
- **name**: An optional name for the endpoint, allowing you to dynamically retrieve the URL without memorizing the route.
- **methods**: An optional list of allowed HTTP request methods (e.g., `GET`, `POST`) for accessing the view. Leave empty for no restrictions.

#### URL Endpoints for `path` and `re_path`

**For `path`:**
- The `path` function allows simple URL endpoints, such as `/` or `/some/long/endpoint`.
- It also supports special endpoints that include dynamic segments in the form of `/some/endpoint/<some_value>`.
  - This allows you to define endpoints with placeholders for dynamic values (e.g., `/user/<user_id>`).
  - The dynamic value (e.g., `user_id`) will be parsed as an additional argument to the corresponding view or it will be provided in `View.kwargs` for class-based views.
  - Example: If the user visits `/some/endpoint/home`, the view will receive `request` and `home` as its keyword arguments.

**For `re_path`:**
- The `re_path` function expects a regular expression (regex) for matching URL patterns.
  - This allows for more flexible and complex URL matching.
  - For instance, `/books/ids/.*` will match any URL starting with `/books/ids/`, followed by any characters.
  - You can use regular expressions to handle a wide variety of patterns and link them to the appropriate views.

Both `path` and `re_path` functions provide powerful mechanisms for routing in Duck, enabling you to create everything from simple to complex URL structures with dynamic and flexible mappings.

This setup ensures efficient and effective route management, which is crucial for building well-structured web applications.

