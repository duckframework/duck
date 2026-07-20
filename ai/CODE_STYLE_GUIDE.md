# Clean Code Style Guide

## Core Principles

Write clean, intentional Python. Code should be easy to read, maintain, and extend.

Follow existing project patterns before introducing new ones. Prefer consistency over personal preference.

Never remove existing docstrings, comments, or documentation unless they are incorrect or obsolete.

Avoid unnecessary complexity. Do not introduce abstractions, files, classes, functions, or variables unless they provide clear value.

---

## Strict Rules

- Always check for and reuse existing components, utilities, helpers, or patterns before creating new ones. Never duplicate existing functionality.
- Never introduce invisible, non-standard, or unexpected characters into files.
- Never hardcode metadata such as brand names, years, emails, locations, URLs, or configuration values. Source these from a central configuration system.
- Always use consistent and predictable patterns across the codebase.
- Never create unused files. Only create files that are referenced and required by the project.
- Keep source files small and focused. When a file becomes too large, split related logic into clearly named modules.
- Never introduce ambiguous or duplicate configuration values.

Example:

```python
# Bad:
class Theme:
    accent = "red"
    accent_color = "red"


# Good:
class Theme:
    accent_color = "red"
```

Avoid conflicting sources of truth:

```python
# Bad:
class Theme:
    accent_color = "red"


THEME = {
    "accent_color": "blue",
}


# Good:
class Theme:
    accent_color = "red"
```

---

## Naming

Use predictable naming conventions.

- `snake_case` for functions, variables, and modules.
- `PascalCase` for classes.
- Use descriptive names. Avoid vague names such as `data`, `thing`, `item`, or `process` unless the context is obvious.
- Do not prefix methods or globals with `_` unless required by Python (`__init__`, etc.).
- Async functions must start with `async_`.

Examples:

```python
# Good

class ProductCard:
    CARD_RADIUS = "10px"

    def build_price_tag(self):
        ...


### Avoid

CARD_RADIUS = "10px"


class ProductCard:
    def _build_price_tag(self):
        ...
```

---

## Formatting

- Follow Black-compatible formatting.
- Maximum line length: 88 characters.
- Use two blank lines between top-level definitions.
- Use one blank line between logical blocks inside functions.
- Use f-strings instead of `.format()` or `%`.
- Add type hints to all public functions and methods.
- Do not add unnecessary whitespace.

Example:

```python
# Good

class Theme:
    """
    Stores application design tokens.
    """

    primary = "#000000"
    surface = "#111111"


# Bad

class Theme:
    """
    Stores application design tokens.
    """

    primary       = "#000000"
    surface       = "#111111"
```

### Module Variables and Constants

- Keep module-level constants and configuration values at the top of the file after imports.
- Group related constants together before classes and functions.
- Use uppercase `SCREAMING_SNAKE_CASE` names for constants.
- Do not hide important configuration values inside functions or classes unless they are class-specific.
- Avoid unnecessary global variables. Only define values globally when they are reused, configurable, or represent a constant.
- Keep global state immutable where possible.

Example:

```python
import os


# API configuration
API_TIMEOUT = 8.0
API_VERSION = "v1"


# External service URLs
GUIDE_SOURCES = {
    "project": "https://example.com/project.md",
    "components": "https://example.com/components.md",
}


def fetch_guide(name: str) -> dict:
    """
    Fetches a guide by name.

    Args:
        name: Guide identifier.

    Returns:
        Guide data.
    """
    ...

---

## Code Organization and Readability

Code must be arranged to be clean, beautiful, and easy to understand. Prioritize readability, clear flow, and maintainability.

Organize files in this order:

1. Imports
2. Module-level constants/configuration
3. Classes
4. Class constants
5. Initialization methods
6. Public methods
7. Helper methods

Example:

```python
import os


# Guide configuration
GUIDE_TIMEOUT = 8.0


class GuideManager:
    """
    Handles loading and retrieving guide documentation.
    """

    # Cache settings
    CACHE_PREFIX = "guide"

    def __init__(self):
        """
        Initializes the guide manager.
        """
        self.cache = {}

    def get_guide(self, name: str) -> str:
        """
        Returns guide content by name.

        Args:
            name: Guide identifier.

        Returns:
            Guide content.
        """
        # Return cached content when available
        if name in self.cache:
            return self.cache[name]

        # Load and cache guide content
        content = self.load_guide(name)
        self.cache[name] = content

        return content
```

### Logical Sections

Use short comments to separate meaningful sections of code. Comments should improve navigation and explain intent.

Good:

```python
# Validate incoming data
data = validate(data)

# Save processed result
save(data)
```

Avoid comments that only describe obvious syntax.

### Visual Flow

Keep related code together and arrange methods in a logical order.

Example:

```python
class UserService:
    """
    Handles user operations.
    """

    # User retrieval operations
    def get_user(self):
        ...

    def get_users(self):
        ...

    # User mutation operations
    def create_user(self):
        ...

    def update_user(self):
        ...
```

Avoid randomly ordered methods or compressed code.

### Spacing

- Use spacing to create readable sections.
- Two blank lines between top-level definitions.
- One blank line between logical blocks inside functions.
- Avoid unnecessary whitespace or compressed formatting.

Code should be written like documentation: clear structure, meaningful grouping, and an obvious flow.

---

## Docstrings

Every module, class, and non-trivial function must have a docstring.

Docstrings are the primary documentation layer.

Rules:

- Always use Google-style docstrings.
- Triple quotes must always be on their own lines.
- Never use inline docstrings.

Bad:

```python
"""Returns a value."""
```

Good:

```python
"""
Returns a calculated value based on the provided input.
"""
```

Docstrings should explain:
- What the code does.
- Why it exists when the purpose is not obvious.
- Arguments and return values where applicable.

Example:

```python
def get_greeting(username: str, fallback: str = "Guest") -> str:
    """
    Returns a personalised greeting for a user.

    Args:
        username: Display name of the user.
        fallback: Value used when no username exists.

    Returns:
        Greeting message.
    """
    name = username or fallback
    return f"Hello, {name}!"
```

Required:

| Target | Docstring |
|---|---|
| Module | Required |
| Class | Required |
| Public function | Required |
| Public method | Required |
| Complex private logic | Recommended |
| Simple helpers | Optional |

---

## Comments

Comments should explain intent, not syntax.

Comments are used as logical section markers inside code.

Rules:

- Every meaningful logical block should have a short comment.
- Comments must be written as action phrases.
- Avoid obvious comments.
- Separator comments are forbidden.

Bad:

```python
# -----------------
# Get user
# -----------------

user = get_user()
```

Good:

```python
# Fetch the authenticated user
user = get_user()
```

Comments should explain why:

```python
# Cache the result to avoid repeated database queries
users = UserService.get_cached_users()
```

---

## Functions and Methods

- Keep functions focused on one responsibility.
- Avoid functions that are too large.
- Extract repeated logic into reusable functions.
- Do not create unnecessary helper functions.
- Prefer readable code over excessive abstraction.

Bad:

```python
def process():
    ...
```

Good:

```python
def calculate_order_total():
    ...
```

---

## Variables

- Avoid unnecessary temporary variables.
- Create variables only when they improve readability.
- Do not create variables that are used once without improving clarity.

Bad:

```python
result = calculate_total()
return result
```

Good:

```python
return calculate_total()
```

---

## Classes

- Classes should represent a clear responsibility.
- Avoid creating classes that only wrap one function.
- Keep related methods together.
- Constants should belong to the class when they are class-specific.

Example:

```python
class Button:
    """
    Represents a reusable UI button component.
    """

    BORDER_RADIUS = "8px"
```

---

## Imports

Use clean and predictable imports.

Rules:

- Prefer absolute imports.
- Separate standard library, third-party, and local imports.
- Import specific objects instead of entire modules.
- Group related imports together.

Example:

```python
import os
import time

from duck.http.response import HttpResponse

from web.ui.components.button import Button
```

Avoid:

```python
from web.ui.components import button
```

Prefer:

```python
from web.ui.components.button import Button
```

---

## Components and UI Code

- Reuse existing components before creating new ones.
- Components should receive prepared data instead of directly querying databases.
- Keep rendering logic separate from data fetching.
- Break large components into smaller focused components.
- Composite components should have unique identifiers where required.

Example:

```python
# Bad

UserCard(user=user_model)


# Good

UserCard(
    user={
        "name": user.name,
        "avatar": user.avatar_url,
    }
)
```

---

## Final Checklist

Before completing code:

- Does it follow existing project patterns?
- Are docstrings present and Google-style?
- Are comments useful?
- Are names clear?
- Is there duplicated functionality?
- Are there unnecessary variables or functions?
- Are configuration values centralized?
- Is the code easy for another developer to understand?
