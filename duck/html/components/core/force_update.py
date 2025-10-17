"""
Module containing a class to force update a component, i.e. force generate
a patch on event binding. Very useful for components updated using JS.

**Usage Example:**

```py
# views.py

from duck.html.components.page import Page
from duck.html.components.button import Button

def myview(request):
    def on_button_click(btn, *_):
        # The following will return update the Button text/innerHTML regardless. Even if it was modified through Javascript.
        return ForceUpdate(btn, ["text"]) # Or return a list of ForceUpdates
    
    # Do some page logic 
    page = Page(request)
    btn = Button(text="Some text")
    
    # Add button to page
    page.add_to_body(btn)
    
    # Bind btn click, but disable any component update by default.
    btn.bind("click", on_button_click, update_self=False, update_targets=[])
    
    # Return page or ComponentResponse
    return page
```
"""

from typing import List

from duck.contrib.sync import iscoroutinefunction
from duck.html.components.core.opcodes import PatchCode
from duck.html.components.core.exceptions import ForceUpdateError, RedundantForceUpdate


def check_force_updates(updates: List["ForceUpdate"]):
    """
    Check if force updates in list are of correct type.
    """
    updates = updates or []
    for update in updates:
        if not isinstance(update, ForceUpdate):
            raise ForceUpdateError(f"Unknown update '{update}', must be an instance of `ForceUpdate` not {type(update)}.")
    

class ForceUpdate:
    """
    Class for applying force updates on HTML components.
    
    Notes:
    - These updates are only limited to components in the DOM/Component tree.
    - You cannot add/remove a component from tree with this approach, rather use the default approach. 
    """
    __slots__ = {"component", "updates"}
    
    def __init__(self, component: "Component", updates: List[str] = None):
        """
        Initialize force update on a component on event.
        
        Args:
            component (Component): The HTML component to target.
            updates (List[str]): List of updates to regenerated. These updates are limited to 'props', 'text', 'inner_html', 'style', 'all'.
        """
        from duck.html.components import Component, InnerComponent
        
        updates = updates or []
        known_updates = ["props", "style", "text", "inner_html", "all"]
        
        if not isinstance(component, Component):
            raise ForceUpdateError(f"Component must be an instance of HtmlComponent not {type(component)}")
        
        if not component.parent:
            raise ForceUpdateError(
                "Force updates can only be applied to components already added in component tree. "
                "Also, this doesn't support root components."
            )
            
        for update in updates:
            if update not in known_updates:
                raise ForceUpdateError(f"Unknown update `{update}`, must be one of {known_updates}.")
        
        if "all" in updates and len(updates) > 1:
            raise RedundantForceUpdate("Update `all` is detected in updates yet the length of updates list is greater than 1.")
        
        if "text" in updates and "inner_html" in updates:
            raise RedundantForceUpdate("Updates `text`, `inner_html` mean the same thing. Either include `text` or `inner_html` not both.")
        
        if ("text" in updates or "inner_html" in updates) and not isinstance(component, InnerComponent):
            raise RedundantForceUpdate("The provided component does not support `text/inner_html` update. Please provide an instance of InnerComponent instead.")
            
        # Save attributes
        self.component = component
        self.updates = updates
    
    async def generate_patch_and_act(self, action):
        """
        Same implementation as `VDOM.diff_and_act` but it only generate patches based on parsed updates (i.e. 'text'/'inner_html', 'props', 'style').
        """
        from duck.html.components import InnerComponent
        
        # Updates 'text' and 'inner_html' is the same thing.
        updates = self.updates
        is_async_action = iscoroutinefunction(action)
        uid = self.component.uid
        
        if "all" in self.updates:
            if isinstance(self.component, InnerComponent):
                updates = ['props', "style", "inner_html"]
            else:
                updates = ['props', "style"]
        
        for update in updates:
            if update == "text" or update == "inner_html":
                # Text update
                patch = [PatchCode.ALTER_TEXT, uid, self.component.inner_html]
                if is_async_action:
                    await action(patch)
                else:
                    action(patch)
                
            # Props update
            if update == "props":
                patch = [PatchCode.REPLACE_PROPS, uid, self.component.props]
                if is_async_action:
                    await action(patch)
                else:
                    action(patch)
                    
            # Style update
            if update == "style":
                patch = [PatchCode.REPLACE_STYLE, uid, self.component.style]
                if is_async_action:
                    await action(patch)
                else:
                    action(patch)
    
    def __str__(self):
        return f'<{self.__class__.__name__} component="{self.component}" updates={self.updates}>'
    
    def __repr__(self):
        return f'<{self.__class__.__name__} component="{self.component}" updates={self.updates}>'
