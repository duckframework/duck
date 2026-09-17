"""
HTML Code Block Component Classes.

These classes represent a code block component that can be embedded within an HTML page.
They provide functionality to display code with options for styling, interactivity, filenames,
collapsing, and copying code to the clipboard.

Classes:
- `CodeContent`: Represents the inner `<code>` element within a `<pre>` tag.
- `CodeBlock`: The base code block component, wrapped in a `<pre>` tag, with a copy button,
  optional filename header, and optional collapsible body.
- `EditableCodeBlock`: Extends `CodeBlock`, allowing the code block to be editable.

Usage:
- `CodeBlock`: Display static code with copy functionality.
- `EditableCodeBlock`: Display editable code with copy functionality.

Example:

```py
code_block = CodeBlock(code="print('Hello, world!')", language="python")
editable_code_block = EditableCodeBlock(code="x = 5", code_style={"color": "blue"})
collapsible_block = CodeBlock(code="...", language="python", filename="main.py", collapsible=True)
```

**Notes**:
- These components are self-contained — no jQuery, Bootstrap, or Bootstrap
  Icons are required. The copy button uses plain SVG icons and vanilla JS.
- Collapsible blocks show a fixed-height preview with a bottom fade and a
  labeled toggle beneath the code, rather than a header icon — this keeps
  the affordance's intent visible instead of hiding it behind a chevron.
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

# Chevron icon for the collapse footer, rotated via CSS when expanded.
DEFAULT_CHEVRON_ICON = (
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" '
    'stroke="currentColor" stroke-width="2">'
    '<path d="M6 9l6 6 6-6"/></svg>'
)

# Vanilla JS copy handler, shared by every CodeBlock instance on the page.
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

# Vanilla JS toggle handler for collapsible code blocks. Toggles an
# "expanded" class on the <pre> element itself, so the preview height,
# fade, footer label, and chevron all react to it via CSS.

COLLAPSE_SCRIPT = """
    function toggleCodeCollapse(button) {
        const codeBlock = button.closest("pre");

        if (!codeBlock) {
            return;
        }

        codeBlock.classList.toggle("expanded");
    }
"""


class CodeContent(InnerComponent):
    """
    Represents the inner `<code>` element in the HTML code block.
    """

    def get_element(self) -> str:
        return "code"


class CodeBlock(InnerComponent):
    """
    Code block HTML component — built on the `<pre>` tag.

    Displays a block of code with a copy-to-clipboard button, an optional
    filename and/or language label, an optional collapsible body, and
    customizable properties for the inner `<code>` tag.

    Example Output:

    ```html
    <pre>
        <div class="code-header">...</div>
        <div class="code-body">
            <code class="language-python">Code text here</code>
            <div class="code-fade"></div>
        </div>
        <div class="code-collapse-footer">Show more</div>
    </pre>
    ```

    Args:
        code (str):
            The code text to display inside the code block.

        language (str, optional):
            Label shown in the header, e.g. "python".
            Also applied to the inner `<code>` tag as a `language-{language}` class.

        filename (str, optional):
            Filename shown in the header, e.g. "main.py".

        collapsible (bool):
            Renders a fixed-height preview with a bottom fade and a labeled
            toggle beneath the code when True.

        collapsed_height (str):
            Preview height while collapsed, e.g. "320px". Defaults to a
            height that reads as a genuine preview rather than a sliver.

        expand_label (str):
            Footer label shown while collapsed. Defaults to "Show more".

        collapse_label (str):
            Footer label shown while expanded. Defaults to "Show less".

        code_props (dict, optional):
            Extra props applied to the `<code>` tag.

        code_style (dict, optional):
            Extra styles applied to the `<code>` tag.

        disable_copy_button (bool):
            Hides the copy button when True.

        idle_icon (str, optional):
            Raw svg shown on the copy button by default.

        success_icon (str, optional):
            Raw svg shown after a successful copy.

        chevron_icon (str, optional):
            Raw svg shown in the collapse footer.

    Attributes:
        code_content (CodeContent): The inner code element inside the `<pre>` tag.
        copy_button (FlexContainer): The clickable copy button, when enabled.
    """

    def get_element(self) -> str:
        return "pre"

    def on_create(self) -> None:
        super().on_create()

        # Set ID and class
        self.id = self.kwargs.get("id", "code-block")
        self.klass = "code-block collapsible" if self.kwargs.get("collapsible") else "code-block"

        # Update the style
        self.style.update({
            "border": f"1px solid {getattr(Theme.current, 'border_color', 'rgba(255, 255, 255, 0.12)')}",
            "border-radius": Theme.current.border_radius,
            "display": "flex",
            "flex-direction": "column",
            "gap": "8px",
            "padding": "10px",
            "width": "100%",
            "background": getattr(Theme.current, "code_background", "black"),
        })

        # Build code content
        self.code_content = self.build_code_content()

        # Add children
        self.add_children(self.build_children())

    def build_children(self) -> list[Any]:
        """
        Builds the code block's children in display order.

        Returns:
            List of components to attach to the `<pre>` element.
        """
        children = []

        if self.has_header():
            children.append(self.build_header())

        # Add code body (code content + fade overlay) and copy script
        children.append(self.build_code_body())
        children.append(Script(inner_html=COPY_SCRIPT))

        # Collapse footer sits below the code, not in the header
        if self.kwargs.get("collapsible"):
            children.append(self.build_collapse_footer())
            children.append(Script(inner_html=COLLAPSE_SCRIPT))

        # Add style
        children.append(self.build_style())

        return children

    def has_header(self) -> bool:
        """
        Checks whether the header row would have any content to show.

        Returns:
            True if a filename, language label, or copy button will be shown.
        """
        return bool(
            self.kwargs.get("filename")
            or self.kwargs.get("language")
            or not self.kwargs.get("disable_copy_button")
        )

    def build_header(self) -> FlexContainer:
        """
        Builds the header row holding the filename, language label, and
        copy button.

        Returns:
            A FlexContainer laying out the header row.
        """
        filename = self.kwargs.get("filename")
        language = self.kwargs.get("language")

        # Initialize header children
        header_children = []

        if filename:
            header_children.append(self.build_filename_label(filename))

        # Initialize trailing children
        trailing_children = []

        if language:
            trailing_children.append(self.build_language_label(language))

        if not self.kwargs.get("disable_copy_button"):
            # Build copy button
            self.copy_button = self.build_copy_button()

            # Add copy button to trailing children
            trailing_children.append(self.copy_button)

        header_children.append(
            FlexContainer(
                klass="code-header-actions",
                style={"align-items": "center", "gap": "8px"},
                children=trailing_children,
            )
        )

        return FlexContainer(
            id="code-header",
            klass="code-header",
            style={
                "justify-content": "space-between" if (filename or language) else "flex-end",
                "align-items": "center",
                "gap": "8px",
            },
            children=header_children,
        )

    def build_filename_label(self, filename: str) -> Any:
        """
        Builds the filename label shown in the header.

        Args:
            filename: Filename to display, e.g. "main.py".

        Returns:
            A Component rendering the filename label.
        """
        return Span(
            text=filename,
            klass="code-filename-label",
            style={
                "color": getattr(Theme.current, "muted_text_color", "rgba(255, 255, 255, 0.6)"),
                "font-size": "0.8rem",
                "font-weight": "500",
            },
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
                "color": getattr(Theme.current, "muted_text_color", "rgba(255, 255, 255, 0.5)"),
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
                "color": getattr(Theme.current, "icon_color", "rgba(255, 255, 255, 0.7)"),
                "transition": "background 0.2s ease, color 0.2s ease",
            },
            children=[
                Span(inner_html=idle_icon, klass="code-copy-icon-idle"),
                Span(inner_html=success_icon, klass="code-copy-icon-success"),
            ],
        )

    def build_code_body(self) -> FlexContainer:
        """
        Wraps the code content in a container that manages the collapsed
        preview height and, when collapsible, a bottom fade overlay.

        Returns:
            A FlexContainer wrapping the code content.
        """
        children = [self.code_content]

        if self.kwargs.get("collapsible"):
            children.append(FlexContainer(klass="code-fade"))

        return FlexContainer(
            klass="code-body",
            style={"position": "relative", "overflow": "hidden"},
            children=children,
        )

    def build_collapse_footer(self) -> FlexContainer:
        """
        Builds the toggle shown beneath the code body when collapsible is
        enabled — a text label stating intent ("Show more" / "Show less")
        plus a chevron, rather than a bare icon in the header.

        Returns:
            A FlexContainer laying out the collapse footer row.
        """
        chevron_icon = self.kwargs.get("chevron_icon", DEFAULT_CHEVRON_ICON)
        expand_label = self.kwargs.get("expand_label", "Show more")
        collapse_label = self.kwargs.get("collapse_label", "Show less")

        return FlexContainer(
            id="code-collapse-btn",
            klass="code-collapse-footer",
            props={
                "onclick": "toggleCodeCollapse(this);",
                "role": "button",
                "tabindex": "0",
                "aria-label": "Toggle full code visibility",
            },
            style={
                "align-items": "center",
                "justify-content": "center",
                "gap": "6px",
                "cursor": "pointer",
                "padding": "6px 0 2px",
                "border-radius": "6px",
            },
            children=[
                Span(text=expand_label, klass="code-collapse-label-more"),
                Span(text=collapse_label, klass="code-collapse-label-less"),
                Span(
                    inner_html=chevron_icon,
                    klass="code-collapse-icon",
                    style={"display": "inline-flex", "align-items": "center"},
                ),
            ],
        )

    def build_style(self) -> Style:
        """
        Builds the copy button, collapse footer, fade, and collapsed/expanded
        state css rules.

        Returns:
            A Style component containing the code block's css rules.
        """
        collapsed_height = self.kwargs.get("collapsed_height", "320px")
        background = getattr(Theme.current, "code_background", "black")
        muted_text = getattr(Theme.current, "muted_text_color", "rgba(255, 255, 255, 0.6)")
        text_color = getattr(Theme.current, "text_color", "white")
        hover_bg = getattr(Theme.current, "hover_background", "rgba(255, 255, 255, 0.1)")

        return Style(
            inner_html=f"""
                .code-copy-btn:hover,
                .code-collapse-footer:hover {{
                    background: {hover_bg};
                }}

                .code-collapse-footer:hover {{
                    color: {text_color};
                }}

                .code-copy-btn .code-copy-icon-success {{
                    display: none;
                }}

                .code-copy-btn.copied .code-copy-icon-idle {{
                    display: none;
                }}

                .code-copy-btn.copied .code-copy-icon-success {{
                    display: inline-flex;
                }}

                .code-block.collapsible .code-body {{
                    max-height: {collapsed_height};
                }}

                .code-block.collapsible.expanded .code-body {{
                    max-height: none;
                }}

                .code-fade {{
                    position: absolute;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    height: 56px;
                    background: linear-gradient(to bottom, transparent, {background});
                    pointer-events: none;
                }}

                .code-block.expanded .code-fade {{
                    display: none !important;
                }}

                .code-collapse-footer {{
                    color: {muted_text};
                    font-size: 0.8rem;
                    font-weight: 500;
                }}

                .code-collapse-label-less {{
                    display: none;
                }}

                .code-block.expanded .code-collapse-label-more {{
                    display: none;
                }}

                .code-block.expanded .code-collapse-label-less {{
                    display: inline;
                }}

                .code-collapse-icon {{
                    transition: transform 0.2s ease;
                }}

                .code-block.expanded .code-collapse-icon {{
                    transform: rotate(180deg);
                }}
            """
        )

    def build_code_content(self) -> CodeContent:
        """
        Builds the inner `<code>` element with the code text and overrides.

        Returns:
            A configured CodeContent component.
        """
        code = self.kwargs.get("code") or ""
        language = self.kwargs.get("language")
        code_props = self.kwargs.get("code_props") or {}
        code_style = {
            "overflow-x": "auto",
            "overflow-y": "hidden",
            "white-space": "pre",
            "color": getattr(Theme.current, "text_color", "white"),
            **(self.kwargs.get("code_style") or {}),
        }

        # Initialize class
        klass = "code-block-content"

        if language:
            klass = f"{klass} language-{language}"

        return CodeContent(
            klass=klass,
            inner_html=code,
            props=code_props,
            style=code_style,
        )


class EditableCodeBlock(CodeBlock):
    """
    Editable version of the CodeBlock component.

    Extends `CodeBlock` and makes the inner `<code>` block content-editable, so
    the displayed code can be edited directly in the browser.

    Example:

    ```py
    editable_code_block = EditableCodeBlock(code="print('Hello, world!')", code_style={"color": "green"})
    ```

    Args:
        code (str): The target code text.
        code_style (dict, optional): Styles applied to the `<code>` element.
    """

    def on_create(self) -> None:
        super().on_create()

        # Set class
        self.klass = f"{self.klass} editable-code-block".strip()

        # Update props
        self.props.update({"contenteditable": "true"})
