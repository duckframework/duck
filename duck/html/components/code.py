"""
HTML Code Component Classes.

These classes represent a code block component that can be embedded within an HTML page.
They provide functionality to display code with options for styling, interactivity, and copying code to the clipboard.

Classes:
- `CodeInner`: Represents the inner `<code>` element within a `<pre>` tag.
- `Code`: The base code block component, wrapped in a `<pre>` tag, with a copy button functionality.
- `EditableCode`: Extends the `Code` component, allowing the code block to be editable.

Usage:
- `Code`: Display static code with copy functionality.
- `EditableCode`: Display editable code with copy functionality.

Example:

```py
code_block = Code(code="print('Hello, world!')", language="python")
editable_code_block = EditableCode(code="x = 5", code_style={"color": "blue"})
```

**Notes**:
- These components are self-contained — no jQuery, Bootstrap, or Bootstrap
  Icons are required. The copy button uses plain SVG icons and vanilla JS.
"""
from typing import Any

from duck.html.components import InnerComponent
from duck.html.components.theme import Theme
from duck.html.components.container import FlexContainer
from duck.html.components.script import Script
from duck.html.components.style import Style
from duck.html.components.span import Span


# Default icons for the copy button's idle and success states
DEFAULT_COPY_ICON = (
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" '
    'stroke="currentColor" stroke-width="1.8">'
    '<rect x="8" y="8" width="12" height="12" rx="2"/>'
    '<path d="M4 16V5a1 1 0 0 1 1-1h11"/></svg>'
)
DEFAULT_COPY_SUCCESS_ICON = (
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" '
    'stroke="currentColor" stroke-width="2">'
    '<path d="M4 12l6 6 10-14"/></svg>'
)

# Vanilla JS copy handler, shared by every Code instance on the page.
# Looks up the sibling <code> element relative to the clicked button,
# so it works regardless of how many code blocks are on the page.
COPY_SCRIPT = """
    function copyCode(button) {
        const codeBlock = button.closest("pre");
        const code = codeBlock ? codeBlock.querySelector("code") : null;

        if (!code) {
            return;
        }

        if (!navigator.clipboard) {
            console.warn("Clipboard API unavailable, copy requires a secure (HTTPS) context.");
            return;
        }

        navigator.clipboard.writeText(code.innerText)
            .then(() => {
                button.classList.add("copied");
                setTimeout(() => button.classList.remove("copied"), 2000);
            })
            .catch((err) => console.error("Failed to copy code: ", err));
    }
"""


class CodeInner(InnerComponent):
    """
    Represents the inner `<code>` element in the HTML code block.
    """

    def get_element(self) -> str:
        return "code"


class Code(InnerComponent):
    """
    Code HTML component — the base component is built on the `<pre>` tag.

    Displays a block of code with a copy-to-clipboard button, an optional
    language label, and customizable properties for the inner `<code>` tag.

    Example Output:

    ```html
    <pre>
        <div class="code-header">...</div>
        <code>Code text here</code>
    </pre>
    ```

    Args:
        code (str): The code text to display inside the code block.
        language (str, optional): Label shown in the header, e.g. "python".
        code_props (dict, optional): Extra props applied to the `<code>` tag.
        code_style (dict, optional): Extra styles applied to the `<code>` tag.
        disable_copy_button (bool): Hides the copy button when True.
        idle_icon (str, optional): Raw svg shown on the copy button by default.
        success_icon (str, optional): Raw svg shown after a successful copy.

    Attributes:
        code_inner (CodeInner): The inner code element inside the `<pre>` tag.
        copy_button (FlexContainer): The clickable copy button, when enabled.
    """

    def get_element(self) -> str:
        return "pre"

    def on_create(self) -> None:
        super().on_create()

        # Base block styling
        self.id = self.kwargs.get("id", "code-block")
        self.klass = "code-block"
        self.style.update({
            "border": "1px solid rgba(255, 255, 255, 0.12)",
            "border-radius": Theme.current.border_radius,
            "display": "flex",
            "flex-direction": "column",
            "gap": "8px",
            "padding": "10px",
            "width": "100%",
            "background": "black",
        })

        # Build the header row, the code content, and the copy script
        self.code_inner = self.build_code_inner()
        self.add_children(self.build_children())

    def build_children(self) -> list[Any]:
        """
        Builds the code block's children in display order.

        Returns:
            List of components to attach to the `<pre>` element.
        """
        children = []

        # Header row, only shown when it would have content
        if self.kwargs.get("language") or not self.kwargs.get("disable_copy_button"):
            children.append(self.build_header())

        children.append(self.code_inner)
        children.append(Script(inner_html=COPY_SCRIPT))
        children.append(self.build_style())

        return children

    def build_header(self) -> FlexContainer:
        """
        Builds the header row holding the language label and copy button.

        Returns:
            A FlexContainer laying out the header row.
        """
        language = self.kwargs.get("language")
        header_children = []

        # Optional language label
        if language:
            header_children.append(self.build_language_label(language))

        # Copy button, unless explicitly disabled
        if not self.kwargs.get("disable_copy_button"):
            self.copy_button = self.build_copy_button()
            header_children.append(self.copy_button)

        return FlexContainer(
            id="code-header",
            klass="code-header",
            style={
                "justify-content": "space-between" if language else "flex-end",
                "align-items": "center",
                "gap": "8px",
            },
            children=header_children,
        )

    def build_language_label(self, language: str) -> Any:
        """
        Builds the small language badge shown in the header.

        Args:
            language: Language name to display, e.g. "python".

        Returns:
            A Component rendering the language label.
        """
        return Span(
            text=language,
            klass="code-language-label",
            style={
                "color": "rgba(255, 255, 255, 0.5)",
                "font-size": "0.75rem",
                "text-transform": "uppercase",
                "letter-spacing": "0.04em",
            },
        )

    def build_copy_button(self) -> FlexContainer:
        """
        Builds the clickable copy button with idle and success icon states.

        Returns:
            A FlexContainer acting as the copy button.
        """
        idle_icon = self.kwargs.get("idle_icon", DEFAULT_COPY_ICON)
        success_icon = self.kwargs.get("success_icon", DEFAULT_COPY_SUCCESS_ICON)

        return FlexContainer(
            id="code-copy-btn",
            klass="code-copy-btn",
            props={
                "onclick": "copyCode(this);",
                "role": "button",
                "tabindex": "0",
                "aria-label": "Copy code",
            },
            style={
                "align-items": "center",
                "justify-content": "center",
                "width": "28px",
                "height": "28px",
                "border-radius": "6px",
                "cursor": "pointer",
                "color": "rgba(255, 255, 255, 0.7)",
                "transition": "background 0.2s ease, color 0.2s ease",
            },
            children=[
                Span(inner_html=idle_icon, klass="code-copy-icon-idle"),
                Span(inner_html=success_icon, klass="code-copy-icon-success"),
            ],
        )

    def build_style(self) -> Style:
        """
        Builds the copy button's hover state and icon-swap styling.

        Returns:
            A Style component containing the copy button's css rules.
        """
        return Style(
            inner_html="""
                .code-copy-btn:hover {
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                }

                .code-copy-btn .code-copy-icon-success {
                    display: none;
                }

                .code-copy-btn.copied .code-copy-icon-idle {
                    display: none;
                }

                .code-copy-btn.copied .code-copy-icon-success {
                    display: inline-flex;
                }
            """
        )

    def build_code_inner(self) -> CodeInner:
        """
        Builds the inner `<code>` element with the code text and overrides.

        Returns:
            A configured CodeInner component.
        """
        code = self.kwargs.get("code") or ""
        code_props = self.kwargs.get("code_props") or {}
        code_style = {"overflow-x": "auto", **(self.kwargs.get("code_style") or {})}

        return CodeInner(
            klass="code-block-inner",
            inner_html=code,
            props=code_props,
            style=code_style,
        )


class EditableCode(Code):
    """
    Editable version of the Code component.

    Extends `Code` and makes the inner `<code>` block content-editable, so
    the displayed code can be edited directly in the browser.

    Example:

    ```py
    editable_code = EditableCode(code="print('Hello, world!')", code_style={"color": "green"})
    ```

    Args:
        code (str): The target code text.
        code_style (dict, optional): Styles applied to the `<code>` element.
    """

    def on_create(self) -> None:
        super().on_create()

        # Mark the block editable, keeping the base "code-block" class
        self.klass = f"{self.klass} editable-code-block".strip()
        self.props.update({"contenteditable": "true"})
