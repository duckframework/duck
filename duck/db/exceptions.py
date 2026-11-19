"""
Custom exceptions for the Duck database.
"""


class DBException(Exception):
    """
    Base class for all Duck database exceptions.
    """


class ValidationError(DBException):
    """
    Raised when a value fails field or model validation.

    Attributes:
        detail: A message, a list of messages, or a mapping of field names
            to lists of messages.
    """

    def __init__(self, detail: str | list[str] | dict[str, list[str]]) -> None:
        """
        Store the error detail.

        Args:
            detail: The error message(s).
        """
        super().__init__(detail)
        self.detail = detail

    @property
    def messages(self) -> list[str]:
        """
        Flatten the error detail into a list of messages.
        """
        # Normalise every detail shape to a flat list
        if isinstance(self.detail, dict):
            return [msg for items in self.detail.values() for msg in items]

        if isinstance(self.detail, list):
            return list(self.detail)

        return [self.detail]

