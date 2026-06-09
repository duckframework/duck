# {py:mod}`duck.backend.django.utils`

```{py:module} duck.backend.django.utils
```

```{autodocx-docstring} duck.backend.django.utils
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`django_to_duck_request <duck.backend.django.utils.django_to_duck_request>`
  - ```{autodocx-docstring} duck.backend.django.utils.django_to_duck_request
    :summary:
    ```
* - {py:obj}`duck_to_django_request <duck.backend.django.utils.duck_to_django_request>`
  - ```{autodocx-docstring} duck.backend.django.utils.duck_to_django_request
    :summary:
    ```
* - {py:obj}`duck_to_django_response <duck.backend.django.utils.duck_to_django_response>`
  - ```{autodocx-docstring} duck.backend.django.utils.duck_to_django_response
    :summary:
    ```
* - {py:obj}`duck_url_to_django_syntax <duck.backend.django.utils.duck_url_to_django_syntax>`
  - ```{autodocx-docstring} duck.backend.django.utils.duck_url_to_django_syntax
    :summary:
    ```
* - {py:obj}`get_raw_django_payload <duck.backend.django.utils.get_raw_django_payload>`
  - ```{autodocx-docstring} duck.backend.django.utils.get_raw_django_payload
    :summary:
    ```
* - {py:obj}`run_django_command <duck.backend.django.utils.run_django_command>`
  - ```{autodocx-docstring} duck.backend.django.utils.run_django_command
    :summary:
    ```
* - {py:obj}`run_from_command_line <duck.backend.django.utils.run_from_command_line>`
  - ```{autodocx-docstring} duck.backend.django.utils.run_from_command_line
    :summary:
    ```
* - {py:obj}`to_django_uploadedfile <duck.backend.django.utils.to_django_uploadedfile>`
  - ```{autodocx-docstring} duck.backend.django.utils.to_django_uploadedfile
    :summary:
    ```
````

### API

````{py:function} django_to_duck_request(django_request: django.http.request.HttpRequest)
:canonical: duck.backend.django.utils.django_to_duck_request

```{autodocx-docstring} duck.backend.django.utils.django_to_duck_request
```
````

````{py:function} duck_to_django_request(request)
:canonical: duck.backend.django.utils.duck_to_django_request

```{autodocx-docstring} duck.backend.django.utils.duck_to_django_request
```
````

````{py:function} duck_to_django_response(response: duck.http.response.HttpResponse)
:canonical: duck.backend.django.utils.duck_to_django_response

```{autodocx-docstring} duck.backend.django.utils.duck_to_django_response
```
````

````{py:function} duck_url_to_django_syntax(url: str) -> str
:canonical: duck.backend.django.utils.duck_url_to_django_syntax

```{autodocx-docstring} duck.backend.django.utils.duck_url_to_django_syntax
```
````

````{py:function} get_raw_django_payload(request: django.http.request.HttpRequest) -> bytes
:canonical: duck.backend.django.utils.get_raw_django_payload

```{autodocx-docstring} duck.backend.django.utils.get_raw_django_payload
```
````

````{py:function} run_django_command(command, *args, **kwargs)
:canonical: duck.backend.django.utils.run_django_command

```{autodocx-docstring} duck.backend.django.utils.run_django_command
```
````

````{py:function} run_from_command_line(command)
:canonical: duck.backend.django.utils.run_from_command_line

```{autodocx-docstring} duck.backend.django.utils.run_from_command_line
```
````

````{py:function} to_django_uploadedfile(fileupload: duck.http.fileuploads.handlers.BaseFileUpload) -> django.core.files.uploadedfile.SimpleUploadedFile
:canonical: duck.backend.django.utils.to_django_uploadedfile

```{autodocx-docstring} duck.backend.django.utils.to_django_uploadedfile
```
````
