"""
Exception classes related to the component system.
"""

class ComponentSystemError(Exception):
    """
    Base exception for component system-related errors.
    """
    pass
    

class HtmlComponentError(ComponentSystemError):
    """
    Exception raised for errors in the HtmlComponent.
    """
    pass
    

class InitializationError(HtmlComponentError):
  """
  Raised upon initialization error. 
  """


class ComponentCopyError(HtmlComponentError):
  """
  Raised on component copy issues.
  """


class ComponentNotLoadedError(HtmlComponentError):
  """
  Raised if component is not loaded yet it is required for component to be loaded.
  """


class FrozenComponentError(HtmlComponentError):
    """
    Raised on attempts to mutate frozen components or data.
    """
    pass


class NoRootError(HtmlComponentError):
    """
    Exception raised for errors when an html component has no root component.
    """
    pass


class NoParentError(HtmlComponentError):
    """
    Exception raised for errors when an html component has no parent.
    """
    pass


class RedundantUpdate(HtmlComponentError):
    """
    Raised when redundant update targets conflict due to shared root.
    """
    pass


class ForceUpdateError(HtmlComponentError):
    """
    Raised when there is an issue in forcily updating a component on event"""
    pass


class RedundantForceUpdate(ForceUpdateError):
    """
    Raised when redundant updates on force updates
    """
    pass


class UnknownEventError(HtmlComponentError):
    """
    Raised when trying to bind a component to unknown event.
    """
    pass



class EventAlreadyBound(HtmlComponentError):
    """
    Raised when trying to bind a component that's already bound.
    """
    pass


class AlreadyInRegistry(HtmlComponentError):
    """
    Raised when trying to add a component already in registry.
    """
    pass


class JavascriptExecutionError(HtmlComponentError):
    """
    Raised when there was a failure in execution of JavaScript on client side due to
    connection-failure or execution error.
    """
    pass
    

class JavascriptExecutionTimedOut(JavascriptExecutionError):
    """
    Raised on timeout whilst executing JavaScript code on client side.
    """
    pass


class ComponentAttributeProtection(HtmlComponentError):
    """
    Raised If protected component attribute is being modified.
    """
