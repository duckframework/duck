"""
CodeShowcase component — a two-column grid of syntax-highlighted
code snippets demonstrating a Duck Framework page and a Lively component.
"""

import html
import keyword
import re

from duck.html.components.container import Container


DUCK_PAGE_CODE = """
# web/ui/pages/home.py

from duck.html.components.page import Page

from web.ui.components.hero import Hero
from web.ui.components.nav import Navbar

class HomePage(Page):
    
    page_title = "Home"
    
    def on_create(self) -> None:
        super().on_create()
        self.set_title(self.page_title)
        self.build_page()
        
    def build_page(self) -> None:
        self.add_to_body([
            Navbar(),
            Hero(title=self.page_title),
        ])
""".strip()


LIVELY_COMPONENT_CODE = """
# web/ui/components/counter.py

from duck.html.components.container import Container
from duck.html.components.button import Button

class Counter(Container):
    def on_create(self) -> None:
        super().on_create()

        # Initialize counter
        self.count = 0

        # Create button
        self.btn = Button(text=str(self.count))

        # Add component to tree
        self.add_child(self.btn)

        # Attach an event handler to button click
        self.btn.bind(
            "click",
            self.handle_click,
            update_self=True,
        )

    async def handle_click(self, *args, **kwargs) -> None:
        self.count += 1
        self.btn.text = str(self.count)
""".strip()


class CodeShowcase(Container):
    """
    Renders two side-by-side code cards with macOS-style window chrome.
    """

    def on_create(self) -> None:
        """
        Builds the two-column code showcase grid.
        """
        super().on_create()
        self.klass = "wc-code-section"

        self.add_children([
            self.build_card("A Duck Page", DUCK_PAGE_CODE),
            self.build_card("A Lively Component", LIVELY_COMPONENT_CODE),
        ])

    @staticmethod
    def highlight_python(code: str) -> str:
        """
        Returns syntax-highlighted Python code as safe HTML.

        Args:
            code: Raw Python source code.

        Returns:
            HTML-safe syntax-highlighted Python code.
        """
        escaped = html.escape(code)

        token_pattern = re.compile(
            r'(?P<comment>#.*?$)'
            r'|(?P<string>(&quot;.*?&quot;|&#x27;.*?&#x27;))'
            r'|(?P<number>\b\d+(?:\.\d+)?\b)'
            r'|(?P<name>\b[A-Za-z_][A-Za-z0-9_]*\b)'
            r'|(?P<pun>[()\[\]{},.:=+\-*/&gt;&lt;]+)',
            re.MULTILINE,
        )

        def replace(match: re.Match[str]) -> str:
            value = match.group(0)

            if match.group("comment"):
                return f'<span class="tok-cmt">{value}</span>'

            if match.group("string"):
                return f'<span class="tok-str">{value}</span>'

            if match.group("number"):
                return f'<span class="tok-num">{value}</span>'

            if match.group("pun"):
                return f'<span class="tok-pun">{value}</span>'

            if match.group("name"):
                if value in keyword.kwlist:
                    return f'<span class="tok-kw">{value}</span>'

                if value in {"True", "False", "None"}:
                    return f'<span class="tok-val">{value}</span>'

                if value[:1].isupper():
                    return f'<span class="tok-cls">{value}</span>'

                return value

            return value

        return token_pattern.sub(replace, escaped)

    def build_card(self, title: str, code: str) -> Container:
        """
        Returns a code card with macOS-style chrome header and syntax body.

        Args:
            title: Label shown in the card header toolbar.
            code: Raw Python source code.

        Returns:
            A Container styled as the code card.
        """
        safe_title = html.escape(title)
        highlighted_code = self.highlight_python(code)
        
        return Container(
            klass="wc-code-card",
            inner_html=(
                '<div class="wc-code-header">'
                '<div class="wc-code-dots">'
                '<div class="wc-code-dot wc-dot-red"></div>'
                '<div class="wc-code-dot wc-dot-yellow"></div>'
                '<div class="wc-code-dot wc-dot-green"></div>'
                '</div>'
                f'<span class="wc-code-title">{safe_title}</span>'
                '</div>'
                f'<pre class="wc-code-body"><code>{highlighted_code}</code></pre>'
            ),
        )