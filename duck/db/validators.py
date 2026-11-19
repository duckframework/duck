"""
Validators for the Duck database.
"""

from __future__ import annotations


import re
import operator
import ipaddress

from typing import Any, Callable, ClassVar

from duck.db.exceptions import ValidationError


IP_PARSERS: dict[str, Callable[[str], Any]] = {
    "ipv4": ipaddress.IPv4Address,
    "ipv6": ipaddress.IPv6Address,
    "both": ipaddress.ip_address,
}


class BaseValidator:
    """
    Base class for all validators.
    """

    def __call__(self, value: Any) -> None:
        """
        Raise ValidationError when the value is invalid.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class RegexValidator(BaseValidator):
    """
    Validate that a value matches a regular expression.
    """

    def __init__(self, pattern: str, message: str = "Enter a valid value.") -> None:
        """
        Compile the pattern.

        Args:
            pattern: Regular expression the value must match.
            message: Error message used on failure.
        """
        self.regex = re.compile(pattern)
        self.message = message

    def __call__(self, value: Any) -> None:
        """
        Raise ValidationError when the value does not match.
        """
        if not self.regex.search(str(value)):
            raise ValidationError(self.message)


class EmailValidator(RegexValidator):
    """
    Validate that a value is a valid email address.
    """

    def __init__(self) -> None:
        """
        Use a simple regex to validate email addresses.
        """
        super().__init__(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", "Enter a valid email address.")


class URLValidator(RegexValidator):
    """
    Validate that a value is a valid URL.
    """

    def __init__(self) -> None:
        """
        Use a simple regex to validate URLs.
        """
        super().__init__(r"^(https?|ftp)://[^\s/$.?#][^\s]*$", "Enter a valid URL.")


class SlugValidator(RegexValidator):
    """
    Validate that a value is a valid slug.
    """

    def __init__(self) -> None:
        """
        Use a simple regex to validate slugs.
        """
        super().__init__(r"^[-a-zA-Z0-9_]+$", "Use only letters, numbers, hyphens and underscores.")


class LimitValidator(BaseValidator):
    """
    Base class for validators that compare a value against a limit.
    """

    compare: ClassVar[Callable[[Any, Any], bool]]
    message: ClassVar[str]

    def __init__(self, limit: Any) -> None:
        """
        Store the limit.

        Args:
            limit: Boundary the measured value is compared against.
        """
        self.limit = limit

    def measure(self, value: Any) -> Any:
        """
        Return the quantity to compare, the value itself by default.
        """
        return value

    def __call__(self, value: Any) -> None:
        """
        Raise ValidationError when the comparison fails.
        """
        if not self.compare(self.measure(value), self.limit): # type: ignore
            raise ValidationError(self.message.format(limit=self.limit))


class MinValueValidator(LimitValidator):
    """
    Require a value greater than or equal to the limit.
    """

    compare = staticmethod(operator.ge)
    message = "Ensure this value is greater than or equal to {limit}."


class MaxValueValidator(LimitValidator):
    """
    Require a value less than or equal to the limit.
    """

    compare = staticmethod(operator.le)
    message = "Ensure this value is less than or equal to {limit}."


class MinLengthValidator(MinValueValidator):
    """
    Require a value with at least the given length.
    """

    message = "Ensure this value has at least {limit} characters."

    def measure(self, value: Any) -> int:
        """
        Return the length of the value.
        """
        return len(value)


class MaxLengthValidator(MaxValueValidator):
    """
    Require a value with at most the given length.
    """

    message = "Ensure this value has at most {limit} characters."

    def measure(self, value: Any) -> int:
        """
        Return the length of the value.
        """
        return len(value)


class IPAddressValidator(BaseValidator):
    """
    Validate IPv4, IPv6 or either kind of address.
    """

    def __init__(self, protocol: str = "both") -> None:
        """
        Select the accepted protocol.

        Args:
            protocol: One of "ipv4", "ipv6" or "both".
        """
        self.parser = IP_PARSERS[protocol]

    def __call__(self, value: Any) -> None:
        """
        Raise ValidationError when the value is not a valid address.
        """
        try:
            self.parser(str(value))
        except ValueError:
            raise ValidationError("Enter a valid IP address.") from None
