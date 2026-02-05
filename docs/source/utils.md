# ⌛ Duck Utilities

The **Duck Utils Module** is a collection of helper submodules designed to enhance functionality within the Duck framework. These utilities simplify various tasks such as data manipulation, logging, request handling, and security operations.

## Features

- **General Utilities**: Common helper functions for everyday operations.
- **Logging Tools**: Improved logging capabilities for debugging.
- **Request Utilities**: Helpers for working with HTTP requests.
- **Security Functions**: Utilities for encryption, hashing, and authentication.

## Submodules

### 1. `caching`

Caching module which leverages the use of diskcache python library. Essential methods mandatory to any Cache class: [set, get, delete, clear]

### 2. `callabletools`

Module for duplicating callables (functions and methods) with the same signature.

This module provides a utility function `duplicate_callable` that can create a 
duplicate of any given callable (function or method) with the same signature. 
The duplicated callable retains the original callable's metadata, such as its 
name and docstring, and can optionally be given a custom name. Additionally, 
a decorator can be applied to the duplicated callable.

### 3. `codesandbox`

Secure Python Code Sandbox:

This script defines a class `SafeCodeSandbox` that provides a secure execution environment
for running arbitrary Python code. It ensures isolation by:
- Running code in a subprocess.
- Blocking dangerous imports and built-ins.
- Restricting system resources like CPU and memory.
- Providing execution time and memory limits to prevent abuse.

### 4. `dateutils`

Date and Time Utilities Module

Provides utility functions for working with dates and times, including formatting,
parsing, calculating time differences, and handling time zones. It also provides functions to get the current time in different formats,
including local time and Greenwich Mean Time (GMT).

### 5. `encrypt`

Compression, encoding, decompressing and decoding module.

### 6. `extraction`

Extraction Utilities Module

This module provides various utilities to extract specific types of information from a given text.
These utilities can be used for extracting URLs, email addresses, phone numbers, hashtags, mentions,
and other patterns that are commonly needed in text processing tasks such as web scraping, form validation,
or text analysis.

Functions include:
- `extract_urls`: Extracts all URLs from a given text.
- `extract_emails`: Extracts all email addresses from a given text.
- `extract_phone_numbers`: Extracts all phone numbers from a given text.
- `extract_hashtags`: Extracts all hashtags from a given text.
- `extract_mentions`: Extracts all mentions (usernames) from a given text.
- `extract_dates`: Extracts all date-like patterns from a given text.
- `extract_currency`: Extracts all currency values from a given text.
- `extract_ips`: Extracts all IP addresses from a given text.
- `extract_social_handles`: Extracts social media handles (like Twitter, Instagram) from a given text.
- `extract_hex_colors`: Extracts all hex color codes from a given text.
- `extract_skus`: Extracts all product SKUs (Stock Keeping Units) from a given text.

### 7. `file`

File Management Utilities Module

Provides utility functions for file operations such as reading, writing, renaming,
moving, and deleting files.

### 8. `filelock`

File lock capabilities module.

### 9. `headers`

Headers utilities module.

### 10. `importer`

Module, object and variable importation module.

### 11. `ipc`

This module provides a simple inter-process communication (IPC) mechanism using file streams.
It allows processes to communicate by writing to and reading from a shared file.

**Functions:**
```
    get_writer() -> FileWriter: Returns a FileWriter object for writing messages.
    get_reader() -> FileReader: Returns a FileReader object for reading messages.
```

**Example Usage:**
```py
    # Process 1
    with get_writer() as writer:
        writer.write_message('Hello from Process 1')
    
    # Process 2
    with get_reader() as reader:
        message = reader.read_message()
        print(message) # Outputs: Hello from Process 1
```

### 12. `object_from_id`

Retrieving an object by using its memory address.

### 13. `object_mapping`

Module contains a function to map keys and values to an object.

### 14. `path`

Module for Path Operations, .e.g path sanitization, manipulations, joining etc.

### 15. `performance`

Performance Utilities Module

Provides functions for measuring code performance, timing code execution, 
and optimizing operations.

### 16. `platform`

Platform targeted tools.

### 17. `port_recorder`

Module for recording and managing used ports within your web application.

### 18. `safe_compare`

Module for safer comparison of sensitive information without having to worry about timing attacks

### 19. `safemarkup`

Module for creating safe strings compatible with both Jinja2 and Django template engines.

This module provides a utility class `SafeMarkup` that subclasses both `markupsafe.Markup`
and Django's `SafeString` classes. This ensures that strings marked as safe using this 
class will be considered safe in both Jinja2 and Django templates. 

Additionally, the module includes an example usage of the `MarkupSafeString` class to demonstrate 
how to create and use safe strings in both template engines.

The function `mark_safe` can also be used to mark strings safe as a decorator to the function which returns a string or to a mere string.

Example:

```py
safe_string = mark_safe("<h1>Hello world</h1>")
	
# or use the following decorator

@mark_safe
def my_func():
	return "<h2>Hello world</h2>"

# Here you can use the safe_string in your templates.
```

### 20. `slug`

Slug Utilities Module

This module provides various utilities for generating, manipulating, and validating slugs.
A slug is a URL-friendly string, typically used in website URLs to represent titles or categories.
These functions allow for tasks such as slug creation from text, slug-to-text conversion, validation,
cleaning, and various string manipulations specific to slugs.

Functions include:
- `slugify`: Converts a string to a URL-friendly slug.
- `unslugify`: Converts a slug back to a human-readable string.
- `is_valid_slug`: Checks if a string is a valid slug.
- `generate_slug_from_string`: Generates a slug from a given string.
- `clean_slug`: Cleans up a slug to ensure it's properly formatted.
- `split_slug`: Splits a slug into individual words.
- `join_slug`: Joins a list of words into a slug.
- `truncate_slug`: Truncates a slug to a specified maximum length.
- `sanitize_slug`: Sanitizes a slug by removing invalid characters.

These utilities are useful for web developers handling slugs for SEO, URLs, or other string-related tasks.

### 21. `sockservers`

Simple implementations of socket servers.

### 22. `ssl`

SSL related tools and utilities.

### 23. `string`

String utilities module providing a variety of functions for common string manipulation tasks for 
example:

```py
text = smart_truncate("Some very long text", cap=12) # Output: Some very...
```

### 24. `timer`

Timer Utility module for scheduling callables.

### 25. `urlcrack`

URLCrack - A lightweight, yet powerful module providing a robust URL class for parsing and manipulating URLs without relying on the `urllib` module. 

This module handles URLs gracefully, even those without a scheme, addressing limitations found in `urllib.parse` and similar libraries.

#### Features:
- Parse and manipulate URLs effortlessly.
- Supports URLs with or without schemes.
- Easily update host, port, query, and other components.

#### Example Usage:

```py
from duck.utils.urlcrack import URL
    
url_obj = URL('duckframework.xyz/some/path?query=something#resource')

# Manipulate the URL object
url_obj.host = "new_site.com"
url_obj.port = 1234  # Set port to None to remove it
    
print(url_obj.to_str()) 
# Outputs: new_site.com:1234/some/path?query=something#resource
```

### 26. `urldecode`

Module containing function for decoding encoded urls.

### 27. `validation`

Validation Utilities Module

This module provides a set of validation functions to check various types of data commonly used in web development
and application processing, such as strings, email addresses, passwords, IP addresses, credit cards, and more.

Functions include:
- `validate_email`: Validates email address format.
- `validate_phone`: Validates phone number format.
- `validate_url`: Validates URL format.
- `validate_username`: Validates username format.
- `validate_ip_address`: Validates IP address (supports both IPv4 and IPv6).
- `validate_hex_color`: Validates a hex color code.
- `validate_credit_card_type`: Checks if the credit card belongs to a certain type (e.g., Visa, MasterCard).
- `validate_json`: Validates if a string is a valid JSON.
- `validate_hexadecimal`: Validates if the string is a valid hexadecimal number.
- `validate_base64`: Validates if the string is a valid Base64 encoded string.
- `validate_password_strength`: Validates if a password meets security requirements.
- `validate_time`: Validates if a time string is in HH:MM format.

### 28. `wildcard`

Filters a list of strings based on a wildcard pattern.
