"""
Warnings for HTML components.
"""

class DeeplyNestedEventBindingWarning(UserWarning):
    """
    Warning indicating that a component has event bindings and is deeply nested in the DOM or component tree.

    This warning is triggered when a component with event listeners is placed at a deep nesting level (e.g., level 6 or greater).
    Deeply nested event bindings may result in slower updates or degraded performance due to increased layout, paint, or event propagation costs.
    Consider refactoring to reduce nesting or optimize event handling.

    Args:
        message (str): The warning message to display.
    """
    pass
