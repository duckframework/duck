# 🗄️️ Database

**Duck** uses **Django's** ORM (Object-Relational Mapper) as its core database system. The ORM simplifies database interactions by providing a high-level API for querying and managing your database, without needing to write raw SQL queries.

For more detailed information about **Django's** ORM, [click here](https://docs.djangoproject.com/en/stable/topics/db/models/).

> By default, **Duck** includes a directory for **Django** integration located at `web/backend/django/duckapp`. This directory contains a pre-configured **Django** project, which allows you to use all the features that **Django** offers. Learn more about **Django** [here](https://www.djangoproject.com/).

## Setup

The recommended way to use **Duck** with **Django's** ORM is by creating a new Django app using the `django startapp ...` command. You can name this app `core` or `base`, which indicates that it is the central or core application responsible for managing and interacting with the database.

For more information about creating and managing Django apps, [click here](https://docs.djangoproject.com/en/stable/ref/applications/).

## Example

```py
from web.backend.django.duckapp.core.models import MyDBModel

# Perform database operations with the model.
```

> **Note:**  
> Don’t forget to add the `core` application in your Django [settings](https://docs.djangoproject.com/en/stable/ref/settings/) file (`web/backend/django/duckapp/duckapp/settings.py`).
> Ensure that `web.backend.django.duckapp.core` is listed under **INSTALLED_APPS** in your settings.

---
The setup provided above gives you the basic configuration to get started with **Duck** and **Django**.

## Running Database Migrations

Running **Django** database migrations is straightforward with the following commands:

```sh
cd myproject
duck django makemigrations core # 'core' is the name of the app that contains your DB models.
duck django migrate
```

> This will apply any changes made to your DB models by migrating them to the database. For more information on database models, check out the [Django Models documentation](https://docs.djangoproject.com/en/stable/topics/db/models/).

## Asynchronous Support

**Duck** enhances the ability to run synchronous code in an asynchronous environment. This is accomplished through the `sync_to_async` function from the module `duck.contrib.sync.smart_async`. This function is different from **asgiref's** `sync_to_async` because it’s specifically optimized for handling more complex synchronous code.

### Sync-To-Async Comparisons

| Feature | Asgiref's `sync_to_async` | Duck's `sync_to_async`               |
|---------|---------------------------|-------------------------------------|
| Threads | Uses a single thread to manage thread-sensitive DB operations | Can utilize multiple threads to handle both thread-sensitive and non-sensitive DB operations |
| Performance | May be slow for handling large DB operations as it uses only one thread | Optimized for high concurrency with multiple threads |
| Atomic/Transactional Operations | Can be slow when handling many requests | Can use multiple threads to perform atomic operations efficiently with `transaction_context` context manager |

> **Note:**  
> We recommend using **Duck's** version of `sync_to_async` over **asgiref's** because it offers better concurrency handling and avoids blocking sequential sync-to-async tasks.

## Admin Page

**Duck** leverages **Django's** built-in admin page since **Django** is already integrated with the project. By default, **Duck** forwards all URLs starting with `/admin` to **Django's** admin panel. This ensures that the Django administration page is accessible via these URLs.

To make the `/admin*` URLs accessible, you need to set `USE_DJANGO = True` in your settings. This activates the original **Django** server to handle requests for the admin page.

To make your DB models appear on the `/admin*` routes, follow these steps:
1. [Import your models](https://docs.djangoproject.com/en/stable/ref/models/fields/) in the `models.py` file of your `core` app (or any other app you choose).
2. [Register your models](https://docs.djangoproject.com/en/stable/ref/contrib/admin/#registering-models) in the Django admin using `admin.site.register()`.
3. [Add the admin URL pattern](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#hooking-adminsite-to-urlconf) in your main app's [`urls.py`](https://docs.djangoproject.com/en/5.2/ref/urls/).
4. Run your **Duck** server with **Django** and visit `http://localhost:8000/admin` to access the admin panel.

**Notes:**
- To log in to the Django admin interface, you need to [create a superuser](https://docs.djangoproject.com/en/stable/topics/auth/default/#creating-a-superuser) using the `duck django createsuperuser` command.
- You don’t need to have extensive knowledge of **Django** to build a functional site; understanding just **Django Models + ORM** (for database interaction) is sufficient. However, other **Django** concepts are optional.

---
> Special thanks to **Django** for creating such a powerful and easy-to-use **ORM**.
