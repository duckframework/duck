# Django Integration

If you have an existing Django project and want production features like HTTPS, HTTP/2, and resumable downloads, Duck makes it easy — no `nginx` setup required.

## Benefits

- Native [HTTP/2 & HTTPS](https://docs.duckframework.com/main/https-and-http2) implementation
- Extra built-in security [middleware](https://docs.duckframework.com/main/middlewares) (DoS, SQLi, etc.)
- Duck and Django run in the same Python environment for faster communication
- Auto-compressed responses
- Resumable large downloads
- Fast, [reactive Lively components](https://docs.duckframework.com/main/lively-components) for a beautiful, responsive UI
- [Free SSL with auto-renewal](https://docs.duckframework.com/main/free-ssl-certificate)
- And more

## Usage

```sh
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

## Notes

- Follow the instructions provided by the `django-add` command carefully.
- Make sure your Django project defines at least one `urlpattern`.
- Once set up, you're good to go!
