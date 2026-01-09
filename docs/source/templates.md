# 📑 Templates

A template is a ...
Duck supports **Django** and **Jinja2** templates. 

## 🛠️ Rendering functions

Duck provides the module `duck.shortcuts` which has the necessary functions for template rendering. The following 
functions can be used to render templates:

1. `render`: The default rendering function, you can switch between **Django** & **Jinja2** by customizing the `engine` argument.
2. `django_render`: Template rendering function explicitly for using **Django** engine.
3. `jinja2_render`: Template rendering function explicitly for using **Jinja2** engine.
4. `async_render`: Render function specifically for asynchronous operations. It's just the same as `render` but for async contexts. 

## ⚙️ Te mplate syntax

1. **Django template syntax**
Here is an example of Django template syntax:

```django
```
For more information, check out [Django's site](https://djangoproject.com/templates) to know more.

2. **Jinja2 template syntax**
Here is an example of Jinja2 template syntax:

```jinja
```
For more information, check out [Jinja2 site](https://openpallets.com/jinja2/templates) to know more.

## 📌 Templates location

To be able to render templates you can just add you templates to directory 
`web/ui/templates`, this is a global template directory and can be customized by setting 
`GLOBAL_TEMPLATE_DIRS` in settings.py file.  

Example:
```py
from duck.shortcuts import render, async_render

def sync_view(request):
    context = {}
    return render(request, "template.html", context, status_code=200)

async def async_view(request):
    context = {}
    return await async_render(request, "template.html", context, status_code=200)
    
```

### 📗 Blueprint templates

If you want to isolate templates per app/blueprint, you can just configure your blueprint to serve these templates. To 
know more on blueprints, [click here](./blueprint.md). By default, all blueprints are configured to serve templates. These templates must be located in 
`templates` directory from your blueprint path. The template directory can be customizable and to render templates from your blueprint, all you need to 
do is to add the blueprint name as a prefix path to the final template. For example, if your blueprint name is `docs` and your template is `index.html` then, the final 
path becomes `docs/index.html`.  

**Example:**
```py
from duck.shortcuts import render, async_render

def sync_view(request):
    context = {}
    return render(request, "some_blueprint/template.html", context, status_code=200)

async def async_view(request):
    context = {}
    return await async_render(request, "some_blueprint/template.html", context, status_code=200)
    
```

---

👉 Next: Learn how to enhance templates with [🏷️Template Tags](./templatetags.md)
