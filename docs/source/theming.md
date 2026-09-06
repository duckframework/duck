# Theming

Duck's theme system provides design tokens (colors, spacing, typography, etc.) as CSS
custom properties, so components reference `var(--theme-<token>)` instead of hardcoded
literals.

## The `Theme` class

A `Theme` is an extensible set of design tokens.

```python
from duck.html.components.theme import Theme

theme = Theme(name="dark")
```

Every `Theme` starts with `Theme.DEFAULTS` — a base set of tokens (`accent_color`,
`border_radius`, `font_family`, and so on). You can layer, override, or add tokens on top
of that.

### Creating and extending themes

```python
# Override or add tokens at construction time
theme = Theme(name="dark", accent_color="#F5C842", border_color="rgba(255,255,255,0.12)")

# Layer on top of an existing theme
brand_theme = Theme(name="brand", base=theme, accent_color="#00FFAA")

# Or derive a new theme from an existing one
brand_theme = theme.extend("brand", accent_color="#00FFAA")

# Add or override tokens after construction
theme.update(spacing="12px", font_size="1.1rem")
```

### Reading tokens

Tokens read like plain attributes:

```python
theme.accent_color   # "#F5C842"
```

Tokens can **not** be set via attribute assignment — `theme.accent_color = "..."` raises
`AttributeError`. Use `update()` or the constructor instead.

`get()` is the non-raising lookup, with an optional default:

```python
theme.get("accent_color")            # "#F5C842"
theme.get("nonexistent", "fallback") # "fallback"
```

### The `dynamic` flag

Every `Theme` instance has a `dynamic` flag (default `False`) that changes what attribute
reads and `get()` return:

| `dynamic` | `theme.accent_color` returns |
|---|---|
| `False` (default) | the literal value — `"#F5C842"` |
| `True` | the CSS var name — `"--theme-accent-color"` |

This lets the same attribute read work in two different contexts: pull the literal value
when you need it directly, or drop the CSS var reference straight into markup/styles when
you want the value to live-update from the stylesheet.

```python
theme = Theme(name="dark", dynamic=True)
theme.accent_color  # "--theme-accent-color"

theme.dynamic = False
theme.accent_color  # "#F5C842"
```

The flag can be flipped at any time on an existing instance — it's not fixed at
construction.

Two ways to control this per-lookup instead of flipping the instance flag:

```python
theme.var("accent_color")                     # "--theme-accent-color" (always, regardless of dynamic)
theme.get("accent_color", dynamic=True)        # "--theme-accent-color" (this call only)
theme.get("accent_color")                      # "#F5C842" (follows the instance's dynamic flag)
```

### Generating CSS

```python
theme.to_css_vars()
# {"--theme-accent-color": "#F5C842", "--theme-border-radius": "12px", ...}

theme.to_style()               # Style component declaring vars under :root
theme.to_style(".theme-dark")  # scoped to a subtree instead of :root
```

`to_css_vars()` and `to_style()` always emit **literal values**, regardless of the
`dynamic` flag — a CSS custom property can't declare itself as its own var reference.

### The active theme

`Theme.current` is a class-level, globally active theme:

```python
Theme.current = dark_theme
active = Theme.current
```

Components and the `Page` component (see below) read `Theme.current` unless told
otherwise.

## Page component auto-theming

The `Page` component can automatically inject the active theme's CSS. This is controlled
by the `add_theme_css` argument, **which defaults to `True`**:

```python
Page(...)                        # add_theme_css=True by default — theme CSS is injected
Page(..., add_theme_css=False)   # opt out — no theme CSS is added
```

With the default `True`, `Page` adds a `<style>` block (via `Theme.current.to_style()`)
to the document head automatically — you don't need to call `to_style()` yourself for the
common case of "use the global theme everywhere."

## Page-specific theming (not yet supported)

There's no built-in per-page theming yet — theming is global-only, via `Theme.current`.

If you need a page to look different, you can approximate page-specific theming manually:

1. Create your global theme as usual, with `dynamic=True`:

   ```python
   Theme.current = Theme(name="global", dynamic=True, accent_color="#F5C842")
   ```

2. For the page that needs different values, create a **separate** `Theme` instance
   (also `dynamic=True`) and add its CSS to that page directly — for example with
   `page.add_to_head(page_theme.to_style())` — instead of assigning it to `Theme.current`.

   ```python
   page_theme = Theme(name="landing", dynamic=True, accent_color="#00FFAA")
   page.add_to_head(page_theme.to_style())
   ```

**Do not set `Theme.current` to the page-specific theme.** `Theme.current` is global, so
doing that would change the theme for every page, not just the one you're working on. Set
`add_theme_css=False` on that `Page` if you don't want the global theme's CSS injected
alongside your page-specific CSS.

This is a manual workaround, not a first-class feature — true page-scoped theming isn't
implemented yet.
