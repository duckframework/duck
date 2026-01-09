# 📘 Blueprints

**Blueprints** are a way to organize routes/urlpatterns for better management. 
Blueprints let you group URL patterns under a single namespace. These are more like **Django apps** or 
**Flask blueprints** but they are a bit different compared to these two. Blueprints are just like independant groupable blocks for storing
your `urlpatterns` in an organized manner.

---

## Blueprint Structure Example

```sh
myproject/  
├── web/
│    ├── myblueprint        # Any name for your blueprint.
│    │    ├── blueprint.py  # Entry python file for your blueprint defination
│    └─  └── views.py  # Views for your blueprint
└── ... # Root project files
```

---

## Example

### settings.py

Blueprints need to be added in settings file to be recognized by **Duck** as shown below:

```py
BLUEPRINTS = [  
    "some_name.blueprint.ProductsBlueprint",  
]
```

### `blueprint.py`

This file contains the blueprint definations and you can create more than
one blueprint in this file.

```py
from duck.routes import Blueprint
from duck.urls import re_path, path
from . import views  

ProductsBlueprint = Blueprint(
    location=__file__,
    name="products", # Name of blueprint
    urlpatterns=[
        path(
            f"/list-products",
            views.product_list_view,
            name="list-products",
            methods=["GET"],
        ),
    ], # The urlpatterns under this blueprint
    prepend_name_to_urls=True,
    enable_template_dir=True,
    enable_static_dir=True,
)

```
From the above example, it shows a blueprint named `products` in a variable called
`ProductsBlueprint` and at has some arguments set.

``` {note}
The url for `list-products` urlpattern will be resolved as `resolve('products.list-products')`.
```

---

## Blueprint arguments

- **location** (str):
    The absolute path to where the blueprint is located.
    It is simply easy to use `__file__` at this point.

- **name** (str):
    A `valid name` for the `blueprint`.This name should be a unique name that differentiate other blueprints from this newly
    created `blueprint`.

- **urlpatterns** (Optional[List[URLPattern]]):
    List of urlpatterns created using `duck.urls.path` or `re_path`. These are just the same as those
    defined in `urls.py`. This does not mean, you should duplicate those ones in `urls.py`, but we are 
    mainly focused on the format and arrangement.
    
    See `urls.py` if you do not know how urlpatterns work.

- **prepend_name_to_urls** (bool):
    Whether to prepend name to urlpatterns. Defaults to True.
    This is a feature for adding `name` of your blueprint to every `urlpattern` defined in `urlpatterns`.
    
    Example:
        Setting `prepend_name_to_urls` to `True` like the example above will result in `/list-products` urlpattern
        to be come end up being `products/list-products`. Set this argument to false if you do not want
        this behavior.

- **template_dir** (str):
    The template directory for the blueprint. This makes it possible for **Duck** to find your `blueprint templates`
    when you use function `duck.shortcuts.render` inside your blueprint views. Disable this for 
    a `blueprint` which doesn't require rendering templates.

- **enable_template_dir** (bool):
    Expose the template dir for template resolving. This enables your blueprint template files
    to be found by `duck.shortcuts.render` function.

- **static_dir** (str):
    The location of static files within the blueprint base directory (same as how `template_dir` works).

- **enable_static_dir** (bool):
    Boolean on whether to enable your blueprint static to be accessible when using functions like `duck.shortcuts.static` or commands like `duck collectstatic`.
                
``` {note}
Creating a `blueprint` is the best thing to do for route, urlpattern or even code organization. Just creating a `blueprint` doesn't 
mean the `blueprint` is automatically available to be accessed, but you need to enable the blueprint by adding it in `settings.py`.
```

---

With blueprints, you can arrange and organize different web endpoints for handling requests and an example 
of such action is creating a blueprint named `api` for handling `API` requests.
