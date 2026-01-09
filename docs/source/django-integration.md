# 🐤 Django Integration with Duck

[![Django](https://img.shields.io/badge/Framework-Django-green?style=for-the-badge&logo=django)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

**Duck** integrates seamlessly with **Django**, allowing you to leverage all of Django’s power **while benefiting from Duck’s modern web server features** ⚡.  

You can access your Django application **directly through Duck**, making it fast, secure, and HTTP/2-ready.

---

## What is Django ?

**Django** is another great python web framework and integrating it into **Duck** can have many benefits.  

Visit [Django Official Site](https://djangoproject.com) for more info.


## 🔄 How It Works

1. **Client sends a request:** A browser or API client initiates a request to the Duck server.  
2. **Duck server receives the request:** Duck handles incoming connections first.  
3. **Forward request to Django:** Duck forwards the request to your Django project running on the same environment.  
4. **Django processes the request:** Django executes its views, middleware, and returns a response.  
5. **Response sent back to client:** Duck sends the Django response back to the client seamlessly.

---

## 🌟 Why Use Duck with Django

- 🚀 **Native HTTP/2 & HTTPS** support  
- 🛡 **Enhanced security middleware**: Protects against DoS, SQLi, and more  
- ⚡ **Same Python environment**: Faster communication between Duck and Django  
- 📦 **Auto-compressed responses** for reduced bandwidth  
- 📂 **Resumable large downloads**  
- ✨ **Fast & reactive UI components**  
- 🔒 **Free SSL with auto-renewal** ([docs](https://duckframework.xyz/documentation/free-ssl-certificate.html))  
- 🔀 **Serving of static & media files**: **Duck** allows serving of **Django** static/media files even in production as **Django** doesn't support this natively in PRODUCTION.
- And much more…

> **Note:** Duck doesn’t handle databases natively. Use Django for models and database operations — Duck can directly utilize Django models in views.  

---

## 🛠️ Integration Steps

Duck provides a simple command for Django integration: `django-add`.

Example:

```sh
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

After running these commands, your Duck server can serve Django routes effortlessly.

---

## ⚡ Notes

- Follow the instructions provided by `django-add` carefully  
- Ensure your Django project defines **at least one `urlpattern`**  
- Once setup, **you’re ready to run your Duck+Django stack!**  

---

✨ With Duck+Django integration, you get the **best of both worlds**: Django’s robust backend and Duck’s modern, async-ready, secure web server 🚀  

---

## Deep Dive

By default, **Duck** forwards all HTTP traffic to Django when `USE_DJANGO = True` in `settings.py`. This allows Django to process requests while still benefiting from Duck’s server capabilities.

However, you can control which framework handles specific routes:

- **`DUCK_EXPLICIT_URLS`** → Routes explicitly handled by Duck.  
- **`DJANGO_SIDE_URLS`** → Routes explicitly handled by Django.

The `duck.backend.django.utils` module provides utilities like `duck_to_django_request` and `django_to_duck_request`, allowing seamless conversion between Duck and Django requests, responses, and objects. 

In most cases, you won't need to use these functions directly—Duck takes care of the integration for you.

---

### Using Django Models in Duck Views

```py
from duck.backend.django.utils import to_django_uploadedfile
from duck.shortcuts import jsonify
from backend.django.duckapp.core.models import VideoUpload  # Import Django model


def video_upload_view(request):
    """
    Duck's simple view for handling video uploads.
    """
    if request.method == "POST":
        
        # Retrieve the uploaded file from the request
        file = request.FILES.get("file")
        
        if file:
            # Convert Duck's file upload object to Django's format
            video_upload = VideoUpload(
                file=to_django_uploadedfile(file)
            )
            
            # Save the file using Django's ORM
            video_upload.save()
            
            # Return a JSON response with status code 200 (Success)
            return jsonify({"status": "success", "message": "Video saved"})
        
        # Return an error response if no file is provided
        return jsonify({"status": "error", "message": "File is required"}, 400)
    
    # Return an error response for unsupported request methods
    return jsonify({"status": "error", "message": "Method not allowed"}, 400)
```

#### Explanation

This example demonstrates how seamlessly Duck interacts with Django models:

1. **Import Dependencies**  
   - Duck utilities for request handling.  
   - A Django model (`VideoUpload`) for storing video uploads.  

2. **View Logic (`video_upload_view`)**  
   - Checks if the request method is **POST**.  
   - Retrieves the uploaded file.  
   - Converts Duck’s file format into Django’s using `to_django_uploadedfile()`.  
   - Saves the file using Django’s ORM.  
   - Returns a **success response** (`200 OK`) or an **error response** (`400 Bad Request`) if no file is provided.  

---

> With Duck’s Django integration, you can enjoy the best of both worlds while keeping your development workflow efficient and straightforward.

---

### Django Configuration

All **Duck** projects comes up with a **Django** project directory and the files within this directory may be 
mofified by **Duck** for security purposes or synchronization.


``` {warning}
Do not modify setting `ALLOWED_HOSTS` if modified by Duck as this is a security feature that Duck uses to make
Django to only accept trusted requests from the `Duck` web application. Rather than doing this, edit the **Duck** project 
`ALLOWED_HOSTS` in Duck root project settings.
```

---

### Security in Django Integration

**Duck** prioritizes security when integrating with **Django**. The Django server is protected by ensuring that only Duck can communicate with it.
If you try to access the **Django** server directly after it has been set up by Duck, the request will be automatically rejected. Duck configures Django to accept requests only from hosts that both Duck and Django know.

By using **Django** as the backend, an additional layer of security is introduced. New requests must pass through both Duck and Django middleware, adding an extra level of protection before reaching the core application.
This layered security approach helps ensure that each request is thoroughly validated, enhancing the overall safety of your application. 🔐

**Duck** modifies the following headers before sending the request to the Django server:  

```py
Host
Origin (if present)
Referer (if present)
```

---

### How can I obtain the headers modified by Duck in their original state? 🤔  

Don't worry—Duck provides a solution!  
When these headers are modified, the original headers will be set with a `D-` prefix. You can easily retrieve the real header by doing this:

```py
header = headers.get("D-Some-Header")
```

*You can also use Duck template tags and filters, which might not be built into Django's template engine, by using the following:*
```django
{% load ducktags %}
```

---

### Running Duck with Django integration

Firstly, run the below command:

```bash
# You can just do duck runserver command without arguments but make sure USE_DJANGO=True in settings.
duck runserver --use-django # or use -dj flag instead
```

By running the above command, **Duck** server will be started on port 
`8000` and `Django` server will be started on port `9999` by default.

---

### Default flow of requests between Duck and Django

The default flow of requests is that all requests received will be processed directly by Duck, meaning, all
requests will not parsed to Django server to be processed. This is because **Duck** is optimized for performance so because 
of the following setting.

```py
DUCK_EXPLICIT_URLS: list = [
    ".*"
] # Optimized fast mode, remove .* for normal optimum flow (processing Duck urls on Django side).
```

The above code will match all URL endpoints and attempt to redirect them to views registered 
by **Duck** in Duck project `urls.py`. There is only an exception if the `DJANGO_SIDE_URLS` setting is set.

Remove the `".*"` in `DUCK_EXPLICIT_URLS` to make all requests to be processed by **Django**. This
means, all the `urlpatterns` you defined within the Duck `urls.py` will be also be available at
**Django** side by default, so, Django is able to come up with a response for the URL endpoints and Duck is able to obtain that
response and send it back to the client.

``` {note}
By redirecting all the requests to be handled by Django, you have introduced a security layer for all your requests
to make them pass through both Duck and Django middlewares. Use this for enhanced security.
```

#### How `DJANGO_SIDE_URLS` works

The setting `DJANGO_SIDE_URLS` works very well for making those requests that **Duck** may attempt
to handle at **Duck** side to be parsed and handled straight at Django side if they meet certain conditions. This is very useful, for example,
you may configure Duck to always handle all requests that have URL matching **Duck registered urlpatterns** and some requests matching urlpatterns that are only
defined in your **Django project** (urlpatterns that Duck doesn't know of, but only Django) to be handled by Django instead.

##### Example

```py
DUCK_EXPLICIT_URLS: list = [
    ".*"
] # Optimized fast mode, remove .* for normal optimum flow (processing Duck urls on Django side).

DJANGO_SIDE_URLS: list[str] = [
    "/admin.*",
    "/x-static.*"
]
```

The above code states that all requests will be handled straight away be **Duck** only if they do not
match any of the `DJANGO_SIDE_URLS`, meaning all request matching this list will be handled at **Django** side.

---

### Django Disallowed Host Error

If you encounter the following error when running the Duck application:

```py
Invalid HTTP_HOST header: 'sq7441iv4yyg1iczep3meyga1lbhpu.gkr.pxyecarnhz.com'. You may need to add 'sq7441iv4yyg1iczep3meyga1lbhpu.gkr.pxyecarnhz.com' to ALLOWED_HOSTS.
```

This typically indicates that another instance of Django launched by Duck is already running. This instance may be configured to allow only specific hosts. To resolve the issue, you need to stop the old Django process before starting the new instance.

#### Example:

To stop the old Django process, you can use the following steps:

1. List the running processes:

    ```sh
    $ ps
      PID TTY          TIME CMD
    4491 pts/0    00:00:00 /data/data/com.termux/files/usr/bin/bash
    21276 pts/0    00:00:02 python
    21285 pts/0    00:00:00 ps
    ```

2. Kill the old Django process (assuming the PID is 21276):

    ```sh
    kill 21276
    ```

Once the old process is stopped, you can continue with your new Django instance.

----

For all these configurations, **Duck** acts a **close reverse-proxy server** for your web application but in a more efficient close
ranged connection.
