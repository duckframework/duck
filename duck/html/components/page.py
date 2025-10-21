'''
# Page Component Module

This module defines the `Page` component class, a robust foundation for building
full HTML pages with advanced SEO, social media integration, accessibility,
performance optimizations, and analytics support.

## Key Features:
- Complete HTML page structure with <html>, <head>, and <body> elements.
- Language and locale configuration through the `lang` attribute and Content-Language meta tag.
- SEO-friendly meta tags: title, description, robots, canonical URL, and pagination (prev/next links).
- Social media metadata support via OpenGraph and Twitter Card tags for rich previews.
- Support for multiple favicons and Apple Touch Icons, accommodating various device requirements.
- Ability to add custom stylesheets and JavaScript files, with async and defer attributes.
- Embedding JSON-LD structured data, with helpers for common types like Article and Product.
- Simple integration for Google Analytics tracking.
- Accessibility improvements by setting appropriate roles and language attributes.
- An `ErrorPage` subclass for quickly creating customizable error pages.

## Recommended Usage Pattern:

To maintain clean, maintainable, and reusable code, it is strongly encouraged
to **create your own page components by subclassing `Page`**. 

Override the `on_create()` method in your subclass to set page-specific metadata,
manage favicons, add scripts/styles, and define body content.

Example subclass:

```py
class HomePage(Page):
    def on_create(self):
        super().on_create()
        self.set_author("My Name")
        self.set_title("Home - MySite")
        self.set_description("Welcome to MySite, the premier platform for ...")
        self.set_favicon("/static/favicon.ico")
        self.set_opengraph(
            title="Home - MySite",
            description="Welcome to MySite, the premier platform for ...",
            url="https://mysite.com",
            image="https://mysite.com/og-image.png",
            type="website",
            site_name="MySite"
        )
        self.set_twitter_card(card="summary_large_image", title="Home - MySite")
        self.set_json_ld({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "url": "https://mysite.com",
            "name": "MySite",
            "description": "Welcome to MySite, the premier platform for ..."
        })
        # Add additional custom head or body components here as needed
```

**Notes**:
- For all page methods, esp those that has `set*` or `add*` prefix e.g. These methods may override existing component if
      called more than once. Not all methods can do this, others may just return the component generated from using that method.
      You can store the components from such methods for later deletion in cases you wanna override in different page.
- To avoid partial page reload and do a fullpage reload on certain page, just set attribute `fullpage_reload` to True.
- Whenever headers like `Set-Cookie` is found in component response, a fullpage reload is triggered. Just modify page's `fullpage_reload_headers`.

By organizing your pages this way, you isolate page-specific logic inside
dedicated classes, making your code easier to maintain, extend, and debug.

---

**Example use case**

```py
# in your views
from duck.shortcuts import to_response

def home(request):
    homepage = HomePage(request=request)
    return to_response(homepage)
```

This module is designed to be flexible and integrates well within Duck projects
or other Python web frameworks employing component-based rendering.
'''
import json

from typing import (
    Dict,
    List,
    Union,
    Optional,
    Callable,
    Tuple,
)

from duck.html.components import (
    Component,
    InnerComponent,
    NoInnerComponent,
    to_component,
)
from duck.html.components.core.exceptions import UnknownEventError, EventAlreadyBound
from duck.html.components.extensions import RequestNotFoundError
from duck.html.components.lively import LivelyScripts
from duck.html.components.script import Script
from duck.html.components.progressbar import ProgressBar
from duck.html.components.snackbar import Snackbar
from duck.html.components.label import Label
from duck.html.components.style import Style
from duck.html.components.modal import Modal
from duck.html.components.paragraph import Paragraph
from duck.utils.lazy import Lazy


class PageError(Exception):
    """
    Raised when required request context is missing.
    """


class Page(InnerComponent):
    """
    Full-featured HTML page component with SEO, social, accessibility, i18n, performance,
    and analytics support.
    """

    def __init__(self, request = None, disable_lively: bool = False, *args, **kwargs):
        """
        Initialize the Page component.
        
        Args:
            request (HttpRequest): The target HTTP request.
            disable_lively (bool): This disables `Lively` components for the page. Defaults to False.
        """
        self._request = request
        self._document_event_bindings = {}
        self._add_doctype_declaration = True
        self.disable_lively = disable_lively
        self.fullpage_reload = False # Set this to enable full page reload.
        self.fullpage_reload_headers = ["set-cookie"] # Headers that requires fullpage reload.
        super().__init__(*args, **kwargs)

    @property
    def request(self) -> "HttpRequest":
        """
        Returns the request object, raises if missing.
        """
        from duck.http.request import HttpRequest # Import module typing definations
        
        request = self._request
        
        if not request:
            # Μaybe this component is used in a template.
            try:
                request = self.get_request_or_raise()
            except RequestNotFoundError:
                raise PageError("Request not provided, further lookup in kwargs or kwargs['context'] failed.")
                
        # Finally, return request.
        return request
        
    def get_request_or_raise(self) -> "HttpRequest":
        """
        Retrieves a request object from component `kwargs` or raise an exception.
        
        Raises:
            RequestNotFoundError:  If the request is not in kwargs or kwargs['context'] (if used in templates).
        """
        # This method overrides the default get_request_or_raise to avoid recursion error when called within the `request` property.
        from duck.http.request import HttpRequest
        
        request: HttpRequest = getattr(self, "_request", None) or self.kwargs.get('request')
        
        if not request:
            # Μaybe this component is used in a template.
            context = self.kwargs.get("context", {})
            request = context.get("request")
        
        if not request:
            raise RequestNotFoundError("Request not found in `kwargs` or kwargs['context'] (if component used in a template).")
            
        # Finally, return request.
        return request
        
    def get_element(self) -> str:
        return "html"
          
    def to_string(self):
        # Override to_string to include doctype declaration.
        return "<!DOCTYPE html>" + super().to_string()
        
    def document_bind(
        self,
        event: str,
        event_handler: Callable,
        force_bind: bool = False,
        update_targets: List["HtmlComponent"] = None,
        update_self: bool = True,
    ) -> None:
        """
        Bind an event handler to the document object.
        
        Args:
            event (str): The name of the event to bind (e.g., "DOMContentLoaded", "DuckNavigated").
            event_handler (Callable): A callable (preferably async) that handles the event.
            force_bind (bool): If True, binds the event even if it's not in the recognized set.
            update_targets (List[HtmlComponent], optional): Other components whose state may be modified 
                when this event is triggered. Defaults to None.
            update_self (bool): Whether this component’s state may change as a result of the event. 
                If False, only other components will be considered for DOM updates. Defaults to True.
    
        Raises:
            UnknownEventError: If the event is not recognized and `force_bind` is False.
            AssertionError: If the event handler is not a callable.
            RedundantUpdate: If any component pair in update_targets share the same root/parent.
            EventAlreadyBound: If event is already bound.
            
        Notes:
        - If `update_self` is False and no `update_targets` are provided, no DOM patch will be sent to the client.
        - This method requires the Lively Component System to be active (i.e., running within a WebSocket context).
        - On navigating to a new page, the following events will be fired:
          - `DOMContentLoaded`
          - `DuckNavigated`  
          You can bind listeners to these events to perform cleanup actions, such as closing open components (dropdowns, modals, etc.).
        
        - Unbinding document event handlers using `document_unbind` **only works** if  no navigation occurs.
          If navigation does happen, the newly visited page will restart following the default  flow
          it was created with, thus, rebinding event handlers (violating the `document_unbind`).
        """
        # Check if component system active
        self.check_component_system_active(
            "Lively Component System is not active. "
            "This is required to enable WebSocket communication for managing lively components."
        )
    
        known_events = {
            "DOMContentLoaded", "DuckNavigated"
        }
        
        if event in self._document_event_bindings:
            raise EventAlreadyBound(f"Event `{event}` already bound, please call `document_unbind` first before rebinding.")
            
        if not force_bind and event not in known_events:
            raise UnknownEventError(
                f"Event `{event}` not recognized. Set `force_bind=True` to bind anyway. Supported: {known_events}."
            )
    
        assert callable(event_handler), "Event handler must be a callable."
        
        sync_targets = set(update_targets or []) # same as update_targets
        
        if update_self:
            sync_targets.add(self)
        
        # Checking for repetitive unnecessary updates.
        for target in sync_targets:
            for other in sync_targets:
                if target is not other:
                    if target.parent == other.parent:
                        raise RedundantUpdate(
                            f"Conflicting updates detected: {repr(target)} and {repr(other)} share the same parent. "
                            "Use only one top-level update target."
                        )
                        
                    if target.get_raw_root() == other.get_raw_root(): # Use get_raw_root() instead of root property for the raw explicit root.
                        raise RedundantUpdate(
                            f"Conflicting updates detected: {repr(target)} and {repr(other)} share the same root. "
                            "Use only one top-level update target."
                        )
                    
        self._document_event_bindings[event] = (
            event_handler,
            update_targets or [],
            update_self,
        )
        
        # Flag event bindings changed.
        self._event_bindings_changed = True
        
    def document_unbind(self, event: str, failsafe: bool = True):
        """
        Remove/unbind an event from the document.
        
        Args:
            event (str): The event name to unbind.
            failsafe (bool, optional): If True (default), silently ignore if the event was never bound.
                If False, raise UnknownEventError if the event does not exist.
    
        Raises
            UnknownEventError: If failsafe is False and the event is not bound.
        
        Notes:
        - Unbinding document event handlers using `document_unbind` **only works** if  no navigation occurs.
          If navigation does happen, the newly visited page will restart following the default  flow
          it was created with, thus, rebinding event handlers (violating the `document_unbind`).
        """
        try:
            del self._document_event_bindings[event]
            # Flag event bindings changed.
            self._event_bindings_changed = True
        except KeyError:
            if not failsafe:
                raise UnknownEventError(f"Event '{event}' is not bound to the page's document: {self}.")
                
    def get_document_event_info(self, event: str) -> Tuple[Callable, List["HtmlComponent"], bool]:
        """
        Returns the event info in form: (event_handler, sync_changes_with, sync_changes_with_self).
        """
        event_info = self._document_event_bindings.get(event, None)
        if not event_info:
            raise UnknownEventError(f"Event `{event}` is not bound to the page's document: {self}.")
        return event_info
        
    def on_create(self):
        from duck.html.components.core.system import LivelyComponentSystem
        
        super().on_create()
        _ = self.request  # Validate request presence
        
        # Add private attributes for storing components, etc.
        self._opengraph_tags = []
        self._twitter_tags = []
        self._stylesheets = []
        self._scripts = []
        self._json_ld_tag = None
        self._analytics_tags = []
        self._keywords = []
        self._author_tag = None
        
        # Base html lang attribute
        self.props["lang"] = "en"

        # Core html structure
        self.head = to_component("", "head")
        self.body = to_component("", "body")
        
        self.body.style["display"] = "flex"
        self.body.style["flex-direction"] = "column"
        
        meta = lambda **kwargs: to_component("", "meta", no_closing_tag=True, **kwargs)

        # Basic meta tags
        self.charset = meta(props={"charset": "UTF-8"})
        self.viewport = meta(props={"name": "viewport", "content": "width=device-width, initial-scale=1.0"})
        self.description = meta(props={"name": "description", "content": ""})
        self.keywords = meta(props={"name": "keywords", "content": ""})
        self.robots = meta(props={"name": "robots", "content": "index, follow"})
        self.lang_http_equiv = meta(props={"http-equiv": "Content-Language", "content": "en"})

        # Title and favicon placeholder
        self.title = to_component("", "title")
        self.favicons: List[Component] = []  # support multiple favicons
        
        # Canonical & pagination links
        self.canonical_link = None
        self.prev_link = None
        self.next_link = None
        
        # Add head and body to page
        self.add_children([self.head, self.body])
        
        # Add head components
        self.add_to_head([
            self.charset,
            self.viewport,
            self.description,
            self.robots,
            self.keywords,
            self.lang_http_equiv,
            self.title,
        ])
        
        if self.disable_lively:
            # Disable Lively scripts and other Lively components.
            return
            
        # Expose the component UID via JS
        # This next line should be first before adding LivelyScripts for these scripts to
        # be able to resolve the Page UID.
        self.add_script(inline=f"window.PAGE_UID='{self.uid}';")
        
        # Add base css style to be used by lively system
        self.base_css = Style(
            text="""
            /* Fade-in on add/replace */
            .patch-fade-in {
              opacity: 0;
              animation: fadeIn 0.1s forwards;
            }
            
            @keyframes fadeIn {
              to { opacity: 1; }
            }
            
            /* Fade-out on remove */
            .patch-fade-out {
              opacity: 1;
              animation: fadeOut 0.1s forwards;
            }
            
            @keyframes fadeOut {
              to { opacity: 0; }
            }
            """
        )
        self.add_to_head(self.base_css)
        
        if LivelyComponentSystem.is_active():
            livelyscripts = LivelyScripts()
            
            # Only add script tags of livelyscripts Div
            scripts = livelyscripts.children.copy()
            
            # Unset the lively scripts parent so that they will be addable to 'head'
            livelyscripts.clear_children()
            self.add_to_head(scripts)
            
        # Add progress bar to show page reloading
        # and snackbar to show network status.
        self.snackbar =  Snackbar(id="page-snackbar", type="info", color="white")
        self.snackbar.style["height"] = ".5px"
        self.snackbar.style["font-size"] = ".5rem"
        
        # Add snackbar label
        self.snackbar_label = Label(id="snackbar-label") 
        self.snackbar_label.style["text-align"] = "center"
        self.snackbar_label.style["margin"] = "auto"
        self.snackbar.add_child(self.snackbar_label)
        
        # Add snackbar and progress bar
        self.progress_bar = ProgressBar(id="page-progress-bar")
        self.progress_bar.style["position"] = "fixed"
        self.progress_bar.style["z-index"] = "5000"
        self.add_to_body([self.snackbar, self.progress_bar])
        
        # Add unsupported browser version banner.
        self.unsupported_browser_banner = Modal(
            title="🌐 Unsupported Browser Detected",
            id="unsupported-browser-banner",
        )
        self.unsupported_browser_banner.style["align-items"] = "center"
        self.unsupported_browser_banner.style["display"] = "none"
        
        # Minimalist dark modal content styling
        self.unsupported_browser_banner.modal_content.style.update({
            "padding": "24px 20px",               # Classic padding
            "text-align": "center",
            "border": "1px solid #ccc"
        })
        
        self.unsupported_browser_info = Paragraph(
            inner_html=(
                "<div style='font-size:2em;margin-bottom:0.3em;'>🚫</div>"
                "<b>Unsupported Browser</b><br>"
                "Your browser isn't supported.<br>"
                "Please update or switch to a modern browser.<br><br>"
                "<a href='https://www.google.com/chrome/' target='_blank' style='color:#4fd1c5;text-decoration:underline;'>Chrome</a> &nbsp;|&nbsp; "
                "<a href='https://www.mozilla.org/firefox/new/' target='_blank' style='color:#fbbf24;text-decoration:underline;'>Firefox</a> &nbsp;|&nbsp; "
                "<a href='https://www.microsoft.com/edge' target='_blank' style='color:#60a5fa;text-decoration:underline;'>Edge</a>"
            ),
            style={
                "text-align": "center",
                "color": "#ccc",
            }
        )
        
        # Set banner content.
        self.unsupported_browser_banner.set_content(self.unsupported_browser_info)
        
        # Add banner.
        self.add_to_body(self.unsupported_browser_banner)
        
        if LivelyComponentSystem.is_active():
            # On syntax error, this means browser is incompatible
            # Show browser incompatibility banner
            self.add_script(
                inline=f"""
                document.addEventListener("DOMContentLoaded", () => {{
                  setTimeout(() => {{
                    if (!window.LIVELY_SCRIPT_COMPATIBLE && window.receivedFullLivelyJs) {{
                      const banner = document.getElementById(`{self.unsupported_browser_banner.id}`);
                      openModal(banner);
                    }}
                  }}, 10); // Delay a little bit
                }});
                """
            )
            
    def set_title(self, title: str):
        """
        Set page title.
        """
        self.title.text = title

    def set_description(self, description: str):
        """
        Set meta description content.
        """
        self.description.props["content"] = description

    def set_author(self, author: str):
        """
        Set the author meta tag.
        
        Args:
            author (str): The author name - personal or organisation name. 
        """
        if self._author_tag and self._author_tag in self.head.children:
            self.head.remove_child(self._author_tag)
        
        # The below line adds meta component to the head
        self._author_tag = self.add_meta(props={"name": "author", "content": author})
        
    def set_keywords(self, keywords: List[str]):
        """
        Set the keywords meta tag.
        
        Args:
            keywords (List[str]): The list of keywords.
        """
        self.keywords.props["content"] = ", ".join(keywords)
        self._keywords = keywords
        
    def set_robots(self, content: str):
        """
        Set robots meta tag content.
        Example: 'noindex, nofollow', 'index, follow', etc.
        """
        self.robots.props["content"] = content
        
    def set_lang(self, lang: str):
        """
        Set HTML lang attribute and Content-Language meta.

        Args:
            lang: Language code like 'en', 'fr', 'es-ES'.
        """
        self.props["lang"] = lang
        self.lang_http_equiv.props["content"] = lang
        
    def set_accessibility(self, lang: Optional[str] = None, role: Optional[str] = None):
        """
        Setup accessibility related props on <html> and <body>.

        Args:
            lang: Set html lang attribute.
            role: Set role attribute on body, e.g., 'main'.
        """
        if lang:
            self.set_lang(lang)
        if role:
            self.body.props["role"] = role
            
    def set_favicon(self, source: str, icon_type: str = "image/png", rel: str = "icon", sizes: Optional[str] = None):
        """
        Add a favicon or icon link tag.

        Args:
            source: URL/path to icon file.
            icon_type: MIME type (e.g. 'image/png', 'image/svg+xml').
            rel: 'icon', 'apple-touch-icon', etc.
            sizes: Optional icon size string like '32x32'.
        
        Returns:
            NoInnerComponent: The generated favicon component.
        """
        props = {"rel": rel, "href": source}
        
        if icon_type:
            props["type"] = icon_type
        
        if sizes:
            props["sizes"] = sizes

        favicon = to_component("", "link", no_closing_tag=True, props=props)
        
        # Append favicon to list and add it to head.
        self.favicons.append(favicon)
        self.add_to_head(favicon)
        
        # Return favicon component.
        return favicon

    def set_favicons(self, icons: List[Dict[str, str]]) -> List[NoInnerComponent]:
        """
        Add multiple favicons/touch icons at once.

        Args:
            icons: List of dicts with keys: href (required), rel, type, sizes.
        
        Returns:
            List[NoInnerComponent]: List of generated favicons.
        """
        icon_comps = []
        
        for icon in icons:
            icon_comp = self.set_favicon(
                icon.get("href"),
                icon.get("type", "image/png"),
                icon.get("rel", "icon"),
                icon.get("sizes"),
            )
            icon_comps.append(icon_comp)
        return icon_comps
        
    def set_canonical(self, url: str):
        """
        Add or update the canonical URL.
        """
        if self.canonical_link and self.canonical_link in self.head.children:
            self.head.remove_child(self.canonical_link)
        
        # Create canonical link component.
        self.canonical_link = to_component("", "link", no_closing_tag=True, props={"rel": "canonical", "href": url})
        self.add_to_head(self.canonical_link)

    def set_pagination(self, prev_url: Optional[str] = None, next_url: Optional[str] = None):
        """
        Add pagination links.

        Args:
            prev_url: URL of previous page.
            next_url: URL of next page.
        """
        if self.prev_link and self.prev_link in self.head.children:
            self.head.remove_child(self.prev_link)
        
        if self.next_link and self.next_link in self.head.children:
            self.head.remove_child(self.next_link)

        if prev_url:
            self.prev_link = to_component("", "link", no_closing_tag=True, props={"rel": "prev", "href": prev_url})
            self.add_to_head(self.prev_link)
        else:
            self.prev_link = None

        if next_url:
            self.next_link = to_component("", "link", no_closing_tag=True, props={"rel": "next", "href": next_url})
            self.add_to_head(self.next_link)
        else:
            self.next_link = None
            
    def set_opengraph(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        image: Optional[str] = None,
        type: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        """
        Set OpenGraph meta tags.
        """
        for tag in self._opengraph_tags:
            if tag in self.head.children:
                self.head.remove_child(tag)
        
        self._opengraph_tags.clear()

        props = {
            "title": title,
            "description": description,
            "url": url,
            "image": image,
            "type": type,
            "site_name": site_name,
        }
        for key, val in props.items():
            if val is not None:
                tag = to_component(
                    "", "meta", no_closing_tag=True,
                    props={"property": f"og:{key}", "content": val}
                )
                self._opengraph_tags.append(tag)
        self.add_to_head(self._opengraph_tags)
        
    def set_twitter_card(
        self,
        card: str = "summary",
        title: Optional[str] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
        site: Optional[str] = None,
        creator: Optional[str] = None,
    ):
        """
        Add Twitter Card meta tags.

        Args:
            card: Type of card (summary, summary_large_image, etc.)
            title: Card title.
            description: Card description.
            image: Image URL.
            site: Twitter @site.
            creator: Twitter @creator.
        """
        for tag in self._twitter_tags:
            if tag in self.head.children:
                self.head.remove_child(tag)
        
        self._twitter_tags.clear()

        props = {
            "twitter:card": card,
            "twitter:title": title,
            "twitter:description": description,
            "twitter:image": image,
            "twitter:site": site,
            "twitter:creator": creator,
        }
        
        for key, val in props.items():
            if val is not None:
                tag = to_component(
                    "", "meta", no_closing_tag=True,
                    props={"name": key, "content": val}
                )
                self._twitter_tags.append(tag)
        self.add_to_head(self._twitter_tags)
        
    def set_json_ld(self, data: Dict):
        """
        Add JSON-LD structured data script tag.
        """
        if not isinstance(data, dict):
            raise ValueError("JSON-LD data must be a dictionary")
        
        if self._json_ld_tag and self._json_ld_tag in self.head.children:
            self.head.remove_child(self._json_ld_tag)
        
        # Create json ld
        json_str = json.dumps(data, ensure_ascii=False)
        self._json_ld_tag = Script(
            inner_html=json_str,
            props={"type": "application/ld+json"}
        )
        
        # Add the json ld component.
        self.add_to_head(self._json_ld_tag)
        
    def set_article_json_ld(self, headline: str, author_name: str, date_published: str, description: str, url: Optional[str] = None):
        """
        Add Article JSON-LD structured data.
        """
        data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": headline,
            "author": {
                "@type": "Person",
                "name": author_name,
            },
            "datePublished": date_published,
            "description": description,
        }
        
        if url:
            data["url"] = url
        
        self.set_json_ld(data)

    def set_product_json_ld(self, name: str, description: str, sku: str, brand: str, price: str, currency: str, availability: str, url: Optional[str] = None, image: Optional[str] = None):
        """
        Add Product JSON-LD structured data.
        """
        data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "description": description,
            "sku": sku,
            "brand": {
                "@type": "Brand",
                "name": brand,
            },
            "offers": {
                "@type": "Offer",
                "price": price,
                "priceCurrency": currency,
                "availability": availability,
                "url": url or "",
            }
        }
        if image:
            data["image"] = image
        self.set_json_ld(data)
        
    def add_meta(self, **kwargs) -> NoInnerComponent:
        """
        Add meta tag to the page's head.
        
        Args:
            **kwargs: Additional keyword arguments to pass to meta component. 
            
        Returns:
            NoInnerComponent: The generated meta component.
        """
        meta = lambda **kwargs: to_component("", "meta", no_closing_tag=True, **kwargs)
        meta = meta(**kwargs)
        self.add_to_head(meta)
        return meta
        
    def add_stylesheet(self, href: str, add_to_noscript: bool = False, **attrs) -> Optional[Component]:
        """
        Add a stylesheet link.

        Args:
            href (str): URL of stylesheet.
            add_to_noscript (bool): Whether to add the stylesheet inside `<noscript>` tags.
            **attrs: Additional attributes like media, integrity, crossorigin.
        
        Returns:
            Optional[Component]: The added component or None (if stylesheet source already exists), you can store this component to remove it later. 
        
        Notes:
        - For the "as" property just parse it as `as_` instead.
        """
        # Avoid duplicates
        for sheet in self._stylesheets:
            if sheet.props.get("href") == href:
                return
                
        # Set stylesheet data
        props = {"rel": "stylesheet", "href": href, "type": "text/css", **attrs}
        
        if "as_" in props:
            val = props["as_"]
            props["as"] = val
            del val
            
        link = to_component("", "link", no_closing_tag=True, props=props)
        
        if add_to_noscript:
            noscript = to_component("", "noscript")
            
            # Add link component to noscript
            noscript.add_child(link)
            
            # Add noscript instead of link component.
            self._stylesheets.append(noscript)
            self.add_to_head(noscript)
            
            # Return the link component.
            return noscript
            
        else: 
            self._stylesheets.append(link)
            self.add_to_head(link)
            
            # Return the link component.
            return link
        
    def add_script(
        self,
        src: Optional[str] = None,
        inline: Optional[str] = None,
        async_: bool = False,
        defer: bool = False,
        **attrs,
    ) -> Optional[Script]:
        """
        Add a script tag.

        Args:
            src: External script URL.
            inline: Inline JS code.
            async_: Async attribute.
            defer: Defer attribute.
            attrs: Other script attributes.
        
        Returns:
            Optional[Script]: The script component or None (if script source already exists), you can store this component to remove it later.
        """
        props = {}
        
        if src:
            props["src"] = src
        if async_:
            props["async"] = "async"
        if defer:
            props["defer"] = "defer"
        
        # Update props
        attrs.setdefault("type", "text/javascript")
        if "source" in attrs:
            raise PageError("Keyword argument `source` not allowed. Defer to using `src` instead.")
        props.update(attrs)

        # Prevent duplicates by src
        if src:
            for script in self._scripts:
                if script.props.get("src") == src:
                    return

        script = Script(inner_html=inline or "", props=props)
        self._scripts.append(script)
        
        # Add script to head.
        self.add_to_head(script)
        
        # Return script component.
        return script
        
    def add_google_analytics(self, tracking_id: str) -> List[Script]:
        """
        Add Google Analytics snippet with the given tracking ID.
        
        Returns:
            List[Script]: Script for the google tag manager and the other is the Google Analytics script.
        
        Notes:
            Make sure you include `https://googletagmanager.com` in CSP script-src if you are using Content Security Policy. 
        Example:
        
        ```py
        add_google_analytics("UA-XXXXX-Y")
        ```
        """
        if not tracking_id:
            return
        
        ga_script = f"""
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{tracking_id}');
        """
        
        # Load GA script async in head, plus inline config
        s0 = self.add_script("https://www.googletagmanager.com/gtag/js?id=" + tracking_id, async_=True)
        s1 = self.add_script(inline=ga_script)
        
        # Return the added scripts.
        return [s0, s1]
        
    def add_to_head(self, child_or_childs: Union[Component, List[Component]]):
        """
        Add component(s) to the head.
        """
        if isinstance(child_or_childs, Component):
            child_or_childs = [child_or_childs]
        self.head.add_children(child_or_childs)

    def add_to_body(self, child_or_childs: Union[Component, List[Component]]):
        """
        Add component(s) to the body.
        """
        if isinstance(child_or_childs, Component):
            child_or_childs = [child_or_childs]
        self.body.add_children(child_or_childs)


class ErrorPage(Page):
    """
    Basic error page with customizable status code and message.
    """

    def __init__(self, status_code: int, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code
        self.message = message

    def on_create(self):
        super().on_create()
        self.set_title(f"Error {self.status_code}")
        self.set_description(self.message)
        self.set_robots("noindex, nofollow")
        self.add_to_body([
            to_component(f"{self.status_code}", "h1"),
            to_component(f"{self.message}", "p"),
        ])
