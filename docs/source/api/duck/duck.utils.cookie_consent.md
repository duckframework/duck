# {py:mod}`duck.utils.cookie_consent`

```{py:module} duck.utils.cookie_consent
```

```{autodocx-docstring} duck.utils.cookie_consent
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_urldecode <duck.utils.cookie_consent._urldecode>`
  - ```{autodocx-docstring} duck.utils.cookie_consent._urldecode
    :summary:
    ```
* - {py:obj}`_urlencode <duck.utils.cookie_consent._urlencode>`
  - ```{autodocx-docstring} duck.utils.cookie_consent._urlencode
    :summary:
    ```
* - {py:obj}`generate_cookie_consent_str <duck.utils.cookie_consent.generate_cookie_consent_str>`
  - ```{autodocx-docstring} duck.utils.cookie_consent.generate_cookie_consent_str
    :summary:
    ```
* - {py:obj}`get_cookie_consents <duck.utils.cookie_consent.get_cookie_consents>`
  - ```{autodocx-docstring} duck.utils.cookie_consent.get_cookie_consents
    :summary:
    ```
* - {py:obj}`has_cookie_consent <duck.utils.cookie_consent.has_cookie_consent>`
  - ```{autodocx-docstring} duck.utils.cookie_consent.has_cookie_consent
    :summary:
    ```
* - {py:obj}`set_cookie_consent <duck.utils.cookie_consent.set_cookie_consent>`
  - ```{autodocx-docstring} duck.utils.cookie_consent.set_cookie_consent
    :summary:
    ```
````

### API

````{py:function} _urldecode(value)
:canonical: duck.utils.cookie_consent._urldecode

```{autodocx-docstring} duck.utils.cookie_consent._urldecode
```
````

````{py:function} _urlencode(value)
:canonical: duck.utils.cookie_consent._urlencode

```{autodocx-docstring} duck.utils.cookie_consent._urlencode
```
````

````{py:function} generate_cookie_consent_str(consents, cookie_name='cookie_consent', max_age=60 * 60 * 24 * 365, path='/', domain=None, secure=False, samesite='Lax', expires=None)
:canonical: duck.utils.cookie_consent.generate_cookie_consent_str

```{autodocx-docstring} duck.utils.cookie_consent.generate_cookie_consent_str
```
````

````{py:function} get_cookie_consents(request, cookie_name='cookie_consent')
:canonical: duck.utils.cookie_consent.get_cookie_consents

```{autodocx-docstring} duck.utils.cookie_consent.get_cookie_consents
```
````

````{py:function} has_cookie_consent(request, category, cookie_name='cookie_consent')
:canonical: duck.utils.cookie_consent.has_cookie_consent

```{autodocx-docstring} duck.utils.cookie_consent.has_cookie_consent
```
````

````{py:function} set_cookie_consent(response, consents, cookie_name='cookie_consent', max_age=60 * 60 * 24 * 365, path='/', domain=None, secure=False, httponly=False, samesite='Lax', expires=None)
:canonical: duck.utils.cookie_consent.set_cookie_consent

```{autodocx-docstring} duck.utils.cookie_consent.set_cookie_consent
```
````
