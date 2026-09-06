"""
Form components module.

Available Forms:
- `Form`: Basic form component.
- `FeedbackForm`: Basic feedback form component.
"""

from duck.html.components import InnerComponent
from duck.html.components.theme import Theme
from duck.html.components.input import Input, CSRFInput
from duck.html.components.textarea import TextArea


class Form(InnerComponent):
    """
    Basic Form component.

    Args:
        action (str): Form URL action.
        method (str): Form method.
        enctype (str): Form enctype
        fields (list[HtmlComponent]): List of html components, usually input html components.
    """

    def get_element(self) -> str:
        return "form"

    def on_create(self):
        super().on_create()

        # Always set form method
        self.props.setdefault("method", self.kwargs.get("method", "post"))

        if "action" in self.kwargs:
            self.props["action"] = self.kwargs.get("action") or "#"

        if "enctype" in self.kwargs:
            self.props["enctype"] = self.kwargs.get("enctype") or "multipart/form-data"

        # Attach fields, tagging each with the shared form-control class
        for field in self.kwargs.get("fields", []):
            existing_class = field.klass or ""
            
            # Update class
            field.klass = f"{existing_class} form-control".strip()
            
            # Add field
            self.add_child(field)


class FeedbackForm(Form):
    """
    Feedback Form component.
    
    Args:
        add_csrf (bool, optional): Whether to add CSRF input source from current request. Defaults to False.
        
    Available Fields:
    - `fullname` (Input): Text Input component
    - `email` (Input): Email Input component.
    - `feedback` (TextArea): TextArea component.
    """

    def on_create(self):
        # Form container styling
        self.klass = "feedback-form form"
        
        # Update style
        self.style.update({
            "display": "flex",
            "flex-direction": "column",
            "gap": "20px",
            "padding": "10px",
            "border-radius": Theme.current.border_radius,
            "border": "1px solid #ccc",
        })

        # Build fields
        self.fullname = Input(
            type="text",
            placeholder="Full Name",
            required=True,
            maxlength=64,
            name="fullname",
        )

        self.email = Input(
            type="email",
            placeholder="Email",
            required=True,
            maxlength=64,
            name="email",
        )

        self.textarea = TextArea(
            placeholder="What is it you like to say?",
            maxlength=255,
            required=True,
            name="feedback",
            props={"rows": "4", "cols": "50"},
        )

        self.submit = Input(
            type="submit",
            value="Submit",
            color=Theme.current.text_color,
            bg_color="green",
            style={"border": "none", "font-size": "1rem"},
        )
        
        # Update fields
        self.kwargs["fields"] = [
            self.fullname,
            self.email,
            self.textarea,
            self.submit,
        ]
        
        # Attach CSRF-protected field set, sourced from the current request
        if self.kwargs.get('add_csrf', False):
            self.fields[0] = CSRFInput(request=self.get_request_or_raise())
        
        # Super create
        super().on_create()
