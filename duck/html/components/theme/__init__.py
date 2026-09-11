"""
Theme system for HTML components.

Provides design tokens (colors, spacing, typography, etc.) as CSS custom
properties so any component can reference var(--theme-<token>)
instead of hardcoded literals. Tokens are open-ended — add any name/value
pair, not just the built-in defaults.
"""

from typing import ClassVar, Optional

from duck.html.components.style import Style


class ThemeMeta(type):
    """
    Metaclass for Theme that provides class-level current theme access.
    """

    @property
    def current(cls) -> "Theme":
        """
        Return the globally active theme.

        Returns:
            The active Theme instance, or DEFAULT_THEME if none was set.
        """
        return _current_theme

    @current.setter
    def current(cls, theme: "Theme") -> None:
        """
        Set the globally active theme.

        Args:
            theme: The Theme instance to activate globally.
        """
        global _current_theme
        _current_theme = theme


class Theme(metaclass=ThemeMeta):
    """
    An extensible set of design tokens.

    Tokens live in a plain dict so new ones can be added at construction
    time or later via update() — useful for overrides, plugin tokens, or
    runtime values. Each token becomes --<CSS_PREFIX>-<token> in CSS.

    Tokens read like plain attributes; writes go through update() or the
    constructor. Attempting to set a token via attribute assignment
    raises, so a typo like theme.border_color = "white" fails loudly
    instead of silently shadowing the token:
    
    ```python
    theme.update(border_color="white")
    theme.border_color # "white"
    theme.border_color = "red" # raises AttributeError
    ```

    The dynamic flag changes what attribute reads return: off, you get
    the literal value; on, you get the CSS var name instead, so the same
    read can be dropped straight into a stylesheet. It can be flipped at
    any time:
    
    ```python
    theme.dynamic = True
    theme.border_color # "--theme-border-color"
    theme.dynamic = False
    theme.border_color # "white"
    ```
    
    var() always returns the CSS var name regardless of the flag, and
    get() takes a per-call dynamic override:
    
    ```python
    theme.var("border_color") # "--theme-border-color"
    theme.get("border_color", dynamic=True) # "--theme-border-color"
    theme.get("border_color") # "white"
    ```

    Access the globally active theme at the class level:
    
    ```python
    active = Theme.current
    Theme.current = my_custom_theme
    ```
    
    """

    CSS_PREFIX: ClassVar[str] = "theme"

    # Real instance state; every other attribute name is treated as a token
    RESERVED_ATTRS: ClassVar[frozenset[str]] = frozenset({"name", "dynamic", "tokens"})

    DEFAULTS: ClassVar[dict[str, str]] = {
        "accent_color": "#F5C842",
        "surface_color": "#111318",
        "link_color": "#8AB4F8",
        "surface_elevated_color": "#1C1F26",
        "text_color": "#F5F5F5",
        "muted_text_color": "rgba(245, 245, 245, 0.6)",
        "border_color": "rgba(255, 255, 255, 0.12)",
        "success_color": "#30D158",
        "warning_color": "#FF9F0A",
        "error_color": "#FF453A",
        "info_color": "#0A84FF",
        "border_radius": "12px",
        "border_radius_sm": "8px",
        "font_family": (
            "-apple-system, BlinkMacSystemFont, 'SF Pro Text', "
            "'Segoe UI', Roboto, sans-serif"
        ),
        "font_size": "1rem",
        "padding": "10px",
        "spacing": "8px",
        "shadow_sm": "0 1px 2px rgba(0, 0, 0, 0.24)",
        "shadow_md": "0 8px 24px rgba(0, 0, 0, 0.28)",
        "transition_fast": "0.15s cubic-bezier(0.4, 0, 0.2, 1)",
        "transition_spring": "0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
    }

    def __init__(
        self,
        name: str = "default",
        base: Optional["Theme"] = None,
        dynamic: bool = False,
        **tokens: str,
    ):
        """
        Initialize a new theme with layered tokens.

        Args:
            name:
                Identifier for this theme.
            
            base:
                Optional Theme to inherit from before applying defaults and explicit overrides.
            
            dynamic:
                Whether attribute reads return the CSS var name
                instead of the literal value. Can be toggled on this
                instance at any time after construction.
            
            **tokens:
                Any token name/value pairs. Unknown names are
                accepted, this is what makes the theme extensible.
        """
        self.name = name
        self.dynamic = dynamic

        # Layer base theme, then class defaults, then explicit overrides
        self.tokens: dict[str, str] = {}

        if base is not None:
            self.tokens.update(base.tokens)

        # Update tokens
        self.tokens.update(self.DEFAULTS)
        self.tokens.update(tokens)

    def __getattr__(self, key: str) -> str:
        """
        Allow attribute-style reads, e.g. theme.accent_color.

        Returns the literal token value, or the CSS var name instead
        when dynamic is on for this instance.

        Args:
            key: Token name to look up.

        Returns:
            The token's literal value, or its CSS var name if dynamic.

        Raises:
            AttributeError: If the token does not exist.
        """
        if key not in self.tokens:
            raise AttributeError(f"Theme '{self.name}' has no token '{key}'")

        if self.dynamic:
            return self.var(key)
            
        return self.tokens[key]

    def __setattr__(self, key: str, value: str) -> None:
        """
        Block attribute-style writes to tokens; only real instance state
        (name, dynamic, tokens) can be set this way.

        Args:
            key: Attribute name being set.
            value: Value being assigned.

        Raises:
            AttributeError: If key isn't reserved instance state — tokens
                must be set via update() or the constructor instead.
        """
        if key in self.RESERVED_ATTRS:
            object.__setattr__(self, key, value)
            return
        
        raise AttributeError(
            f"Cannot set token '{key}' via attribute assignment; "
            f"use theme.update({key}=...) instead."
        )

    def var(self, key: str) -> str:
        """
        Return a token's CSS var name, regardless of the dynamic flag.

        Args:
            key: Token name to look up.

        Returns:
            The CSS var name, e.g. "--theme-border-color".

        Raises:
            AttributeError: If the token does not exist.
        """
        if key not in self.tokens:
            raise AttributeError(f"Theme '{self.name}' has no token '{key}'")

        css_name = key.replace("_", "-")
        return f"--{self.CSS_PREFIX}-{css_name}"

    def get(self, key: str, default: str = "", dynamic: Optional[bool] = None) -> str:
        """
        Return a token's value or CSS var name safely, without raising.

        Args:
            key: Token name to look up.
            default: Fallback if the token is missing.
            dynamic: Overrides this instance's dynamic flag for just this
                call. Leave unset to use the instance's current setting.

        Returns:
            The literal value, the CSS var name, or default if missing.
        """
        if key not in self.tokens:
            return default
        
        # Whether to return dynamic vars
        use_dynamic = self.dynamic if dynamic is None else dynamic
        
        if use_dynamic:
            return self.var(key)
            
        return self.tokens[key]

    def update(self, **tokens: str) -> "Theme":
        """
        Add new tokens or override existing ones after construction.

        Args:
            **tokens: Token name/value pairs to merge in.

        Returns:
            self, for chaining.
        """
        self.tokens.update(tokens)
        return self

    def extend(self, name: str, **overrides: str) -> "Theme":
        """
        Create a new Theme inheriting this theme's tokens.

        Args:
            name: Name for the derived theme.
            **overrides: Tokens to change or add.

        Returns:
            A new Theme instance; this theme is left unchanged.
        """
        return Theme(name=name, base=self, **overrides)

    def to_css_vars(self) -> dict[str, str]:
        """
        Convert every token into a CSS custom property.

        Always uses literal values regardless of the dynamic flag, since
        a CSS custom property can't declare itself as its own var name.

        Returns:
            Dict mapping --<CSS_PREFIX>-<token> to its literal value.
        """
        css_vars = {}

        for token, value in self.tokens.items():
            css_name = token.replace("_", "-")
            css_vars[f"--{self.CSS_PREFIX}-{css_name}"] = value

        # Return final css vars.
        return css_vars

    def to_style(self, selector: str = ":root") -> Style:
        """
        Build a Style component declaring this theme's CSS variables.

        Args:
            selector: CSS selector to scope variables under. Defaults to
                :root for global theming. Pass .theme-dark to scope to a
                subtree.

        Returns:
            A Style component, ready for page.add_to_head().
        """
        declarations = "\n".join(
            f"  {prop}: {value};"
            for prop, value in self.to_css_vars().items()
        )
        return Style(inner_html=f"{selector} {{\n{declarations}\n}}")


# Sensible default so components theme themselves out of the box
DEFAULT_THEME = Theme()

# Module-level theme registry for global access
_current_theme: Theme = DEFAULT_THEME
