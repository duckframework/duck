# 🏷️ Template Tags & Filters

[![Jinja2](https://img.shields.io/badge/Engine-Jinja2-blue?style=for-the-badge&logo=jinja)](#)  
[![Django](https://img.shields.io/badge/Engine-Django-green?style=for-the-badge&logo=django)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

Duck allows you to **extend templates** using **template tags** and **filters**, supporting both **Jinja2** and **Django template engines**.  

This gives you the flexibility to **write reusable logic directly in templates** 🌟.

---

## 📝 Syntax Overview

### Default Template Tag

- **Django:** `{% sometag 'inputs' %}` — `inputs` are the arguments.  
- **Jinja2:** `{{ sometag('inputs') }}` — `inputs` are the arguments.  

### Block Template Tag

- **Django:** `{% sometag %} Some data {% endsometag %}`  
- **Jinja2:** ` {% sometag %} Some data {% endsometag %} `

### Template Filter

- **Django:** `{{ somevalue | somefilter }}`  
- **Jinja2:** `{{ somevalue | somefilter }}`
---

## 🏷️ Quick Cheatsheet

| Feature                         | Django Syntax                       | Jinja2 Syntax                         |
|-----------------------------------|--------------------------------------------|--------------------------------------------|
| Default Template Tag | `{% tag 'args' %}`                   | `{{ tag('args') }}`                     |
| Block Template Tag    | `{% tag %} ... {% endtag %}`  | `{% tag %} ... {% endtag %}`  |
| Template Filter            |  `{{ value | filter }}`                  | `{{ value | filter }}`                  |

---

## 👨‍💻 Example Usage

```py
# templatetags.py
from duck.template.templatetags import TemplateTag, TemplateFilter, BlockTemplateTag

# Define a regular template tag
def mytag(arg1, context):
    # Custom logic here
    return "some data"

# Define a template filter
def myfilter(data):
    # Process data
    return data

# Define a block template tag
def myblocktag(content):
    # Process block content
    return content

# Register your tags and filters
TEMPLATETAGS = [
    TemplateTag("name_here", mytag, takes_context=True),  # takes_context defaults to False
    TemplateFilter("name_here", myfilter),
    BlockTemplateTag("name_here", myblocktag)
]
```

---

## ⚡ Notes

- For **Django templates** rendered via `django.shortcuts.render`, insert this at the **top of your template**:

```django
{% load ducktags %}
```

- This is only required if the **Django project is integrated into Duck**.  
- If using **Duck’s internal `render` functions** or classes like `TemplateResponse`, no extra loading is needed.  
- Use this primarily for **standalone Django templates** unrelated to Duck’s template system.  

---

✨ With Duck template tags & filters, you can **write cleaner templates**, **reuse logic**, and **mix powerful Python code into templates** effortlessly 🏷️  

