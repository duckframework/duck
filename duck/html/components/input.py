"""
Input components module.
"""

from duck.html.components import (
    NoInnerComponent,
    Theme,
)
from duck.html.components.container import FlexContainer
from duck.html.components.label import Label


class BaseInput(NoInnerComponent):
    """
    Base Input component.
    """
    def get_element(self):
        return "input"
    
    def on_create(self):
         super().on_create()
         style = {
            "padding": "10px",
            "border": "1px solid #ccc",
            "border-radius": Theme.border_radius,
            "font-size": Theme.normal_font_size,
         }
         self.style.setdefaults(style)


class Input(BaseInput):
    """
    Input component.
    
    Args:
         type (str): The type of input, e.g. text, url, etc.
         name (str): Name of the input component.
         placeholder (str): Placeholder for input component.
         required (bool): Whether the field is required or not.
         maxlength (int): The maximum allowed characters.
         minlength (int): The minimum allowed characters.
         disabled (bool): Whether input is disabled.
         
     """
    def on_create(self):
        super().on_create()
        self.props["min-width"] = "50%"
        self.props["min-height"] = "60px"
        
        if "type" in self.kwargs:
            self.props["type"] = self.kwargs.get('type')
            
        if "value" in self.kwargs:
             self.props["value"] = self.kwargs.get("value")
             
        if "name" in self.kwargs:
            self.props["name"] = self.kwargs.get('name') or ''
        
        if "placeholder" in self.kwargs:
            placeholder = self.kwargs.get('placeholder') or ''
            self.props["placeholder"] = placeholder
       
        if "required" in self.kwargs:
            self.props["required"] = "true"
       
        if "maxlength" in self.kwargs:
           self.props["maxlength"] = str(self.kwargs.get('maxlength')) or ''  
        
        if "minlength" in self.kwargs:
           self.props["minlength"] = str(self.kwargs.get('minlength')) or ''  
        
        if "disabled" in self.kwargs:
            self.props["disabled"] = "true" if self.kwargs.get("disabled") else "false"


class InputWithLabel(FlexContainer):
    """
    InputWithLabel component which contains a label alongside an input component.
    
    Args:
        label_text (str): Text for the label
        input (HtmlComponent): Any html component (e.g fileinput.FileDragAndDrop), preferrebly Input component.
        
    Example Usage:
    
    ```py
    fullname = InputWithLabel(
        label_text="Full Name", # Or use label_html
        input=Input(
            type="text",
            name="fullname",
            placeholder="Full Name",
            required=True,
            maxlength=64,
        )
    )
        
    email = InputWithLabel(
        label_text="Email",
        input=Input(
            type="email",
            name="email",
            placeholder="Email",
            required=True,
            maxlength=64,
        )
    )
    ```
    """
    def on_create(self):
        super().on_create()
        self.style["gap"] = "10px"
        self.style["flex-direction"] = "column"
        
        if "label_html" in self.kwargs:
            label_html = self.kwargs.get('label_html')
            self.label = Label(inner_html=label_html)
            self.add_child(self.label)
        
        elif "label_text" in self.kwargs:
            label_text = self.kwargs.get('label_text')
            self.label = Label(text=label_text)
            self.add_child(self.label)
        
        if "input" in self.kwargs:
            self.inputfield = self.kwargs.get('input')
            if self.inputfield:
                self.add_child(self.inputfield)


class CSRFInput(Input):
    """
    Csrf Input component - This component is useful in situations where you don't want to use the
    `csrf_token` tag. You only need to parse a request to generate `csrfmiddleware` field so as to avoid
    `cross site request forgery attacks`.
    """
    def __init__(self, request: "HttpRequest"):
        from duck.http.request import HttpRequest
        
        self.request: HttpRequest = request
        self.add_to_registry = False # we don't care about live changes.
        
        # Super initilization after setting attributes
        super().__init__()
        
    def on_create(self):
        super().on_create()
        from duck.shortcuts import csrf_token
        
        # Empty all styles and props
        self.style.clear()
        self.props.clear()
        
        # Set some useful properties
        self.props["type"] = "hidden"
        self.props["name"] = 'csrfmiddlewaretoken'
        self.props["value"] = csrf_token(self.request)
