"""
Import your views here, make sure to include them in __all__ list. This
This ensures your views don't get removed when different formatters
formatting this python file.  

**Note:** Adding views to __all__ is not mandatory.
"""
# eg: from .home import home_view

from duck.views import View
from duck.shortcuts import static, to_response
from duck.html.components import LiveResult
from duck.html.components.container import FlexContainer
from duck.html.components.heading import Heading
from duck.html.components.button import Button, FlatButton
from duck.html.components.label import Label
from duck.html.components.page import Page
from duck.html.components.link import Link
from duck.html.components.code import Code


# Source code for the counter app.
SOURCE_CODE = """
from duck.html.components import LiveResult
from duck.html.components.container import FlexContainer
from duck.html.components.heading import Heading
from duck.html.components.button import Button
from duck.html.components.label import Label
from duck.html.components.page import Page


class HomePage(Page):
    def on_create(self):
        super().on_create()
        self.style["font-family"] = "system-ui"
        self.set_title("Simple Counter App")
        
        # Initialize counter
        self.counter = 0
        
        def on_btn_click(btn, *_):
            self.counter += 1
            
        # Container for components alignment
        self.container = FlexContainer()
        self.container.style["gap"] = "5px"
        self.container.style["flex-direction"] = "column"
        self.container.style["align-items"] = "center"
        self.container.style["justify-content"] = "center"
        self.container.style["padding"] = "20px"
        
        # Add topheading
        self.heading = Heading("h1", text="Counter App", color="#bbb")
        self.container.add_child(self.heading)
        
        # Add label
        self.label = Label(text=LiveResult(lambda: self.counter))
        self.label.color = "black"
        self.label.style["font-size"] = "1.5rem"
        self.container.add_child(self.label)
        
        # Initialize button
        self.btn = Button(text="Increment")
        self.btn.color = "white"
        self.btn.bg_color = "green"
        self.btn.style["padding"] = "20px"
        self.btn.style["font-size"] = "1.2rem"
        
        # Bind button to onclick event
        self.btn.bind(
            "click",
            on_btn_click,
            update_targets=[self.label],
            update_self=False,
        )
        
        # Add button to container
        self.container.add_child(self.btn)
        
        # Add container to page's body
        self.add_to_body(self.container)

"""

class HomePage(Page):
    def on_create(self):
        super().on_create()
        self.id = "counterapp-page"
        self.style["font-family"] = "system-ui"
        self.set_title("Simple Counter App")
        
        # Add bootstrap icons + prism.css
        self.add_stylesheet(href=static("counterapp/css/bootstrap.min.css"))
        self.add_stylesheet(href=static("counterapp/css/bootstrap-icons.min.css"))
        self.add_stylesheet(href=static("counterapp/css/prism.css"))
        
        # Add prism.js for code highlighting
        self.add_script(src=static("counterapp/js/prism.js"), defer=True)
        
        # Add bootstrap js
        self.add_script(src=static("counterapp/js/bootstrap.min.js"), defer=True)
        
        # Add JQuery
        self.add_script(src=static("counterapp/js/jquery-3.7.1.min.js"))
        
        # Initialize counter
        self.counter = 0
        
        def on_btn_click(btn, *_):
            if btn == self.btn:
                # Increment button
                self.counter += 1
            else:
                if self.code.style.get("display") == "none":
                    btn.text = "Hide source"
                    del self.code.style["display"]
                else:
                    btn.text = "View source"
                    self.code.style["display"] = "none"
                    
        # Container for components alignment
        self.container = FlexContainer()
        self.container.style["gap"] = "5px"
        self.container.style["flex-direction"] = "column"
        self.container.style["align-items"] = "center"
        self.container.style["justify-content"] = "center"
        self.container.style["padding"] = "20px"
        
        # Add topheading
        self.heading = Heading("h1", text="Counter App", color="#bbb")
        self.container.add_child(self.heading)
        
        # Add label
        self.label = Label(text=LiveResult(lambda: self.counter))
        self.label.color = "black"
        self.label.style["font-size"] = "1.5rem"
        self.container.add_child(self.label)
        
        # Initialize button
        self.btn = Button(text="Increment")
        self.btn.color = "white"
        self.btn.bg_color = "green"
        self.btn.style["padding"] = "20px"
        self.btn.style["font-size"] = "1.2rem"
        
        # Bind button to onclick event
        self.btn.bind(
            "click",
            on_btn_click,
            update_targets=[self.label],
            update_self=False,
        )
        
        # Add button to container
        self.container.add_child(self.btn)
        
        # Add link for viewing source
        self.view_src_btn = FlatButton(text="View source", color="green")
        self.container.add_child(self.view_src_btn)
        
        # Add source code
        self.code = Code(code=SOURCE_CODE, color="#ccc")
        self.code.style["display"] = "none"
        self.code.code_inner.klass = "language-python"
        self.container.add_child(self.code)
        
        # Bind an event to view source
        self.view_src_btn.bind(
            "click",
            on_btn_click,
            update_self=False,
            update_targets=[self.container]
        )
        
        # Add container to page's body
        self.add_to_body(self.container)


class HomeView(View):
    def run(self):
        # This method must return an HTTP response or data that
        # can be converted into one.
        page = HomePage(self.request)
        return to_response(page)
