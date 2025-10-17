"""
Table of Contents HTML Component.

This module defines two components:
1. `TableOfContentsSection` - Represents a content section with a heading and body.
2. `TableOfContents` - Generates a navigable table of contents.

Each `TableOfContentsSection` is added to the `TableOfContents` component, which 
automatically creates a clickable list of links for navigation.
"""

from duck.utils.slug import slugify
from duck.html.components import to_component
from duck.html.components.container import FlexContainer
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph
from duck.html.components.link import Link


class TableOfContentsSection(FlexContainer):
    """
    Represents a section in the Table of Contents.

    Each section consists of a heading (anchor link target) and body content.

    Args:
    - `heading` (str): The heading of the section, which will be linked in the Table of Contents.
    - `body` (str): The main content of the section, which can be plain text or HTML.
    """
    
    def on_create(self):
        super().on_create()
        self.style["flex-direction"] = "column"
        self.style["margin-top"] = "10px"
        self.klass = "toc-section"
        
        self.heading = None
        self.body = None

        # Add heading if provided
        if "heading" in self.kwargs:
            heading_text = self.kwargs.get("heading") or ""
            self.heading = Heading("h3", inner_html=heading_text, klass="toc-heading", id=slugify(heading_text))
            self.add_child(self.heading)
        
        # Add body content if provided
        if "body" in self.kwargs:
            body_content = self.kwargs.get("body") or ""
            self.body = Paragraph(inner_html=body_content, klass="toc-body") # Allow html rendering
            self.add_child(self.body)


class TableOfContents(FlexContainer):
    """
    Table of Contents Component.

    This component generates a navigable list of links to `TableOfContentsSection` instances.

    Args:
        title (str): The title displayed at the top of the Table of Contents. Defaults to "Table of Contents".
    """

    def on_create(self):
        super().on_create()
        self.style["flex-direction"] = "column"
        self.style["gap"] = "3px"
        self.klass = "table-of-contents"

        # Set title
        title_text = self.kwargs.get("title", "Table of Contents")
        self.title_heading = Heading("h1", text=title_text, klass="toc-title")
        
        # Create list container for quick navigation links
        self.list_container = to_component("", tag="ul", klass="toc-list")
        
        # Add title and list container to the component
        super().add_child(self.title_heading)
        super().add_child(self.list_container)

    def add_child(self, child: TableOfContentsSection, list_style: str = "circle"):
         """
         Adds a `TableOfContentsSection` to the Table of Contents.

        This method also creates a clickable link for the section heading.

         Args:
            section (TableOfContentsSection): The section to add.
            list_style (str): The CSS list-style type for the navigation items. Defaults to "circle".
         """
         self.add_section(child, list_style)
        
    def add_section(self, section: TableOfContentsSection, list_style: str = "circle"):
        """
        Adds a `TableOfContentsSection` to the Table of Contents.

        This method also creates a clickable link for the section heading.

        Args:
            section (TableOfContentsSection): The section to add.
            list_style (str): The CSS list-style type for the navigation items. Defaults to "circle".
        """
        assert isinstance(section, TableOfContentsSection), "Only a TableOfContentsSection component is allowed"

        if section.heading:
            heading_text = section.heading.inner_html
            heading_link = Link(text=heading_text)
            heading_link.style["text-decoration"] = "none"
            heading_link.props["href"] = f"#{section.heading.props.get('id', '')}"

            list_item = to_component("", tag="li")
            list_item.style["list-style"] = list_style
            list_item.add_child(heading_link)
            self.list_container.add_child(list_item)

        # Add the section to the Table of Contents
        super().add_child(section)
