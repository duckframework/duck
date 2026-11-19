"""
Duck Field definitions that compile to SQLAlchemy columns.
"""
import re
import uuid
import enum
import json

from typing import Any, ClassVar, Dict
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    Interval,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    Time,
    Uuid,
)
from sqlalchemy import ForeignKey as SAForeignKey
from sqlalchemy.orm import MappedColumn, mapped_column, relationship

from duck.db.exceptions import ValidationError
from duck.db.validators import (
    IP_PARSERS,
    EmailValidator,
    URLValidator,
    SlugValidator,
    IPAddressValidator,
    MaxLengthValidator,
    MinLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from duck.contrib.storage.backends import StorageBackend, ProgressCallback, StoredFile


# Sentinel for "no default supplied", since None is a valid default
UNSET = object()

# Sentinel for "empty" values, used in blank validation
EMPTY_VALUES: tuple = (None, "", [], (), {})

# SQLite only autoincrements plain INTEGER primary keys
BIG_INTEGER = BigInteger().with_variant(Integer, "sqlite")

# Default validators for common field types
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")


def utcnow() -> datetime:
    """
    Return the current timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


def current_time() -> time:
    """
    Return the current UTC time of day.
    """
    return utcnow().time()


def normalize_choices(choices: Any) -> list[tuple[Any, str]]:
    """
    Convert supported choice formats into a list of (value, label) tuples.

    Args:
        choices: An Enum class, a mapping, or an iterable of values or
            (value, label) pairs.

    Returns:
        The normalised list of choices, empty when none were given.
    """
    if choices is None:
        return []

    # Enum members become (value, readable name)
    if isinstance(choices, type) and issubclass(choices, enum.Enum):
        return [(m.value, m.name.replace("_", " ").title()) for m in choices]

    if isinstance(choices, Mapping):
        return list(choices.items())

    return [
        tuple(item) if isinstance(item, (tuple, list)) else (item, str(item))
        for item in choices
    ]


class BaseField:
    """
    Base class for all model fields.

    A field is a declarative description of a column plus UI metadata. The
    model class replaces each field with a SQLAlchemy column when it is
    created, while the field itself stays available through `Model.fields`.

    Args:
        primary_key: Whether the column is the primary key.
        null: Whether the database column accepts NULL.
        blank: Whether validation accepts empty values.
        default: Python-side default, a value or a zero-argument callable.
        unique: Whether the column has a unique constraint.
        index: Whether the column is indexed.
        db_column: Column name in the database, defaults to the attribute.
        db_comment: Comment stored on the database column.
        server_default: Server-side default expression.
        onupdate: Python-side value or callable applied on every UPDATE.
        choices: Enum class, mapping, or iterable of values or pairs.
        validators: Extra callables that raise ValidationError.
        editable: Whether forms should allow editing the field.
        label: Human-readable name, derived from the attribute by default.
        help_text: Guidance text shown beside the input.
        placeholder: Placeholder text shown inside the input.
        error_messages: Overrides for the default validation messages.
        **extra: Free-form attributes forwarded to the UI input, e.g.
            `autocomplete="email"` or `css_class="wide"`.
    """

    column_type: ClassVar[Any] = None
    input_type: ClassVar[str] = "text"
    autoincrement: ClassVar[Any] = "auto"
    is_column: ClassVar[bool] = True
    default_messages: ClassVar[dict[str, str]] = {
        "null": "This field cannot be null.",
        "blank": "This field cannot be blank.",
        "invalid": "Enter a valid value.",
        "invalid_choice": "{value!r} is not a valid choice.",
    }

    def __init__(
        self,
        *,
        primary_key: bool = False,
        null: bool = False,
        blank: bool = False,
        default: Any = UNSET,
        unique: bool = False,
        index: bool = False,
        db_column: str | None = None,
        db_comment: str | None = None,
        server_default: Any = None,
        onupdate: Any = None,
        choices: Any = None,
        validators: Iterable[Callable[[Any], None]] | None = None,
        editable: bool = True,
        label: str | None = None,
        help_text: str = "",
        placeholder: str = "",
        error_messages: Mapping[str, str] | None = None,
        **extra: Any,
    ) -> None:
        """
        Store the field configuration.
        """
        self.primary_key = primary_key
        self.null = null
        self.blank = blank
        self.default = default
        self.unique = unique
        self.index = index
        self.db_column = db_column
        self.db_comment = db_comment
        self.server_default = server_default
        self.onupdate = onupdate
        self.choices = normalize_choices(choices)
        self.editable = editable
        self.label = label
        self.help_text = help_text
        self.placeholder = placeholder
        self.extra = extra

        # Merge messages from every class in the hierarchy
        self.messages = self.collect_messages()
        self.messages.update(error_messages or {})

        # Combine default validators with any user-supplied ones
        self.validators = [*self.get_default_validators(), *(validators or [])]

    @classmethod
    def collect_messages(cls) -> Dict[str, str]:
        """
        Merge `default_messages` across the class hierarchy.
        """
        messages: Dict[str, str] = {}

        for klass in reversed(cls.__mro__):
            messages.update(vars(klass).get("default_messages", {}))

        return messages

    @property
    def has_default(self) -> bool:
        """
        Whether a value is filled in automatically on insert.
        """
        return self.default is not UNSET or self.server_default is not None

    @property
    def required(self) -> bool:
        """
        Whether forms must supply a value.
        """
        return not self.blank

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Return validators implied by the field's own options.
        """
        return []

    def get_choices(self) -> list[tuple[Any, str]]:
        """
        Return the allowed (value, label) pairs, empty when unrestricted.
        """
        return self.choices

    def get_label(self, name: str) -> str:
        """
        Return the human-readable label for the attribute name.
        """
        return self.label or name.replace("_", " ").capitalize()

    def fail(self, code: str, **context: Any) -> None:
        """
        Raise ValidationError with the message registered under a code.

        Args:
            code: Key in `self.messages`.
            **context: Values interpolated into the message.

        Raises:
            ValidationError: Always.
        """
        raise ValidationError(self.messages[code].format(**context))

    def parse(self, parser: Callable[[Any], Any], value: Any) -> Any:
        """
        Convert a raw value with a parser, mapping failures to ValidationError.

        Args:
            parser: Callable converting the raw value.
            value: Raw value, where None and "" both mean empty.

        Returns:
            The parsed value, or None for empty input.
        """
        if value is None or (isinstance(value, str) and value == ""):
            return None

        try:
            return parser(value)
        except (TypeError, ValueError, ArithmeticError):
            self.fail("invalid")

    def to_python(self, value: Any) -> Any:
        """
        Coerce a raw value into the field's Python type.
        """
        return value

    def validate(self, value: Any) -> None:
        """
        Check nullability, blankness and choices.

        Args:
            value: Value already converted by `to_python`.

        Raises:
            ValidationError: If the value is not acceptable.
        """
        choices = self.get_choices()

        if choices and value not in EMPTY_VALUES:
            if value not in {choice[0] for choice in choices}:
                self.fail("invalid_choice", value=value)

        if value is None and not self.null:
            self.fail("null")

        if not self.blank and value in EMPTY_VALUES:
            self.fail("blank")

    def run_validators(self, value: Any) -> None:
        """
        Run every validator and report all failures together.

        Args:
            value: Value already converted by `to_python`.

        Raises:
            ValidationError: Collecting every validator message.
        """
        if value in EMPTY_VALUES:
            return

        # Initialise a list of error messages to collect from validators
        errors: list[str] = []

        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as exc:
                errors.extend(exc.messages)

        if errors:
            raise ValidationError(errors)

    def clean(self, value: Any) -> Any:
        """
        Convert and fully validate a value.

        Args:
            value: Raw value to clean.

        Returns:
            The cleaned Python value.
        """
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)

        return value

    def get_column_type(self) -> Any:
        """
        Return the SQLAlchemy type, or None to infer it from other arguments.
        """
        return self.column_type

    def get_column_args(self, name: str) -> list[Any]:
        """
        Return extra positional column arguments such as constraints.

        Args:
            name: Attribute name the field is bound to.
        """
        return []

    def get_column_kwargs(self, name: str) -> dict[str, Any]:
        """
        Build the keyword arguments passed to `mapped_column`.

        Args:
            name: Attribute name the field is bound to.
        """
        kwargs: dict[str, Any] = {
            "primary_key": self.primary_key,
            "nullable": self.null,
            "unique": self.unique,
            "index": self.index,
            "autoincrement": self.autoincrement,
        }

        # None is a valid default, so it is checked against the sentinel
        if self.default is not UNSET:
            kwargs["default"] = self.default

        # Only pass the remaining optional arguments when provided
        optional = {
            "server_default": self.server_default,
            "onupdate": self.onupdate,
            "comment": self.db_comment,
            "name": self.db_column,
        }

        # Filter out None values so that SQLAlchemy can infer the column name
        kwargs.update({k: v for k, v in optional.items() if v is not None})

        return kwargs

    def to_column(self, name: str) -> MappedColumn:
        """
        Build the SQLAlchemy mapped column for this field.

        Args:
            name: Attribute name the field is bound to.

        Returns:
            A configured mapped column.
        """
        column_type = self.get_column_type()
        type_args = [] if column_type is None else [column_type]

        return mapped_column(
            *type_args, *self.get_column_args(name), **self.get_column_kwargs(name)
        )

    def contribute(self, owner: type, name: str) -> dict[str, Any]:
        """
        Return the class attributes this field adds to its model.

        Args:
            owner: Model class being created.
            name: Attribute name the field is bound to.

        Returns:
            A mapping of attribute names to SQLAlchemy objects.
        """
        return {name: self.to_column(name)}

    def collect_attrs(self) -> dict[str, Any]:
        """
        Collect HTML-style input attributes implied by the field options.
        """
        attrs: dict[str, Any] = {}

        if self.placeholder:
            attrs["placeholder"] = self.placeholder

        if self.required:
            attrs["required"] = True

        if not self.editable:
            attrs["readonly"] = True

        return attrs

    def get_input_attrs(self) -> dict[str, Any]:
        """
        Return input attributes, with user supplied extras taking priority.
        """
        return {**self.collect_attrs(), **self.extra}

    def describe(self, name: str) -> dict[str, Any]:
        """
        Describe the field for forms and other UI code.

        Args:
            name: Attribute name the field is bound to.

        Returns:
            A dictionary of label, input type, choices and input attributes.
        """
        choices = self.get_choices()

        return {
            "name": name,
            "label": self.get_label(name),
            "field_type": type(self).__name__,
            "input_type": "select" if choices else self.input_type,
            "required": self.required,
            "editable": self.editable,
            "help_text": self.help_text,
            "placeholder": self.placeholder,
            "choices": choices,
            "attrs": self.get_input_attrs(),
        }


class IntegerField(BaseField):
    """
    Integer column with optional range validation.

    Args:
        min_value: Smallest accepted value.
        max_value: Largest accepted value.
        **options: Options forwarded to `BaseField`.
    """

    column_type = Integer
    input_type = "number"
    positive: ClassVar[bool] = False

    def __init__(self, min_value: int | None = None, max_value: int | None = None, **options: Any) -> None:
        """
        Store the range limits.
        """
        if self.positive and min_value is None:
            min_value = 0

        # Store the limits for later use in validators and input attributes
        self.min_value = min_value
        self.max_value = max_value

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add range validators for the configured limits.
        """
        validators: list[Callable[[Any], None]] = []

        if self.min_value is not None:
            validators.append(MinValueValidator(self.min_value))

        if self.max_value is not None:
            validators.append(MaxValueValidator(self.max_value))

        return validators

    def get_column_args(self, name: str) -> list[Any]:
        """
        Enforce non-negative values in the database for positive fields.
        """
        args = super().get_column_args(name)

        if self.positive:
            column = self.db_column or name

            # Add a check constraint to the column to enforce non-negative values
            args.append(CheckConstraint(f"{column} >= 0", name=f"{name}_positive"))

        return args

    def to_python(self, value: Any) -> int | None:
        """
        Convert the value to an int.
        """
        return self.parse(int, value)

    def collect_attrs(self) -> dict[str, Any]:
        """
        Add numeric input attributes.
        """
        attrs = super().collect_attrs()
        attrs["step"] = 1

        if self.min_value is not None:
            attrs["min"] = self.min_value

        if self.max_value is not None:
            attrs["max"] = self.max_value

        return attrs


class SmallIntegerField(IntegerField):
    """
    Small integer column.
    """

    column_type = SmallInteger


class BigIntegerField(IntegerField):
    """
    Big integer column.
    """

    column_type = BIG_INTEGER


class PositiveIntegerField(IntegerField):
    """
    Integer column that only accepts values of zero or more.
    """

    positive = True


class PositiveSmallIntegerField(SmallIntegerField):
    """
    Small integer column that only accepts values of zero or more.
    """

    positive = True


class PositiveBigIntegerField(BigIntegerField):
    """
    Big integer column that only accepts values of zero or more.
    """

    positive = True


class AutoField(IntegerField):
    """
    Auto-incrementing integer primary key.
    """

    autoincrement = True

    def __init__(self, **options: Any) -> None:
        """
        Default to a read-only primary key.
        """
        options.setdefault("primary_key", True)
        options.setdefault("blank", True)
        options.setdefault("editable", False)

        # Pass the remaining options to the base field
        super().__init__(**options)

    @property
    def has_default(self) -> bool:
        """
        The database always assigns the value.
        """
        return True


class SmallAutoField(AutoField):
    """
    Auto-incrementing small integer primary key.
    """

    column_type = SmallInteger


class BigAutoField(AutoField):
    """
    Auto-incrementing big integer primary key.
    """

    column_type = BIG_INTEGER


class FloatField(BaseField):
    """
    Floating point column.
    """

    column_type = Float
    input_type = "number"

    def to_python(self, value: Any) -> float | None:
        """
        Convert the value to a float.
        """
        return self.parse(float, value)

    def collect_attrs(self) -> dict[str, Any]:
        """
        Allow any decimal step in number inputs.
        """
        attrs = super().collect_attrs()
        attrs["step"] = "any"

        # Return the attributes
        return attrs


class DecimalField(BaseField):
    """
    Fixed-precision decimal column.

    Args:
        max_digits: Total number of digits stored.
        decimal_places: Number of digits after the decimal point.
        **options: Options forwarded to `BaseField`.
    """

    input_type = "number"
    default_max_digits: ClassVar[int] = 10
    default_decimal_places: ClassVar[int] = 2

    def __init__(
        self,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        **options: Any,
    ) -> None:
        """
        Store the precision settings.
        """
        self.max_digits = max_digits or self.default_max_digits
        self.decimal_places = (
            self.default_decimal_places if decimal_places is None else decimal_places
        )

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_column_type(self) -> Numeric:
        """
        Return a Numeric type with the configured precision.
        """
        return Numeric(self.max_digits, self.decimal_places)

    def to_python(self, value: Any) -> Decimal | None:
        """
        Convert the value to a Decimal.
        """
        if isinstance(value, Decimal):
            return value

        return self.parse(lambda raw: Decimal(str(raw)), value)

    def collect_attrs(self) -> dict[str, Any]:
        """
        Set the input step to the smallest representable amount.
        """
        attrs = super().collect_attrs()
        attrs["step"] = f"{Decimal(1).scaleb(-self.decimal_places):f}"

        # Return the attributes
        return attrs


class BooleanField(BaseField):
    """
    Boolean column that defaults to False.
    """

    column_type = Boolean
    input_type = "checkbox"

    # Define the set of values that are considered true and false
    TRUE_VALUES: ClassVar[frozenset[str]] = frozenset(
        {"true", "1", "yes", "on", "t", "y"}
    )
    FALSE_VALUES: ClassVar[frozenset[str]] = frozenset(
        {"false", "0", "no", "off", "f", "n", ""}
    )

    def __init__(self, default: Any = False, **options: Any) -> None:
        """
        Make the field optional in forms, as unchecked means False.
        """
        options.setdefault("blank", True)

        # Pass the remaining options to the base field
        super().__init__(default=default, **options)

    def to_python(self, value: Any) -> bool | None:
        """
        Convert common truthy and falsy strings to a bool.
        """
        if value is None or isinstance(value, bool):
            return value

        # Normalize the value to a lowercase string for comparison
        text = str(value).strip().lower()

        if text in self.TRUE_VALUES:
            return True

        if text in self.FALSE_VALUES:
            return False

        self.fail("invalid")


class CharField(BaseField):
    """
    Length-limited text column.

    Args:
        max_length: Maximum number of characters, class default if omitted.
        min_length: Minimum number of characters.
        **options: Options forwarded to `BaseField`.
    """

    default_max_length: ClassVar[int] = 255

    def __init__(
        self,
        max_length: int | None = None,
        min_length: int | None = None,
        **options: Any,
    ) -> None:
        """
        Store the length limits.
        """
        self.max_length = max_length or self.default_max_length
        self.min_length = min_length

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_column_type(self) -> String:
        """
        Return a String type with the configured length.
        """
        return String(self.max_length)

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add length validators.
        """
        validators: list[Callable[[Any], None]] = [MaxLengthValidator(self.max_length)]

        if self.min_length is not None:
            validators.append(MinLengthValidator(self.min_length))

        return validators

    def to_python(self, value: Any) -> str | None:
        """
        Convert the value to a string.
        """
        return None if value is None else str(value)

    def collect_attrs(self) -> dict[str, Any]:
        """
        Add length attributes.
        """
        attrs = super().collect_attrs()
        attrs["maxlength"] = self.max_length

        if self.min_length is not None:
            attrs["minlength"] = self.min_length

        # Return the final attributes
        return attrs


class TextField(BaseField):
    """
    Unbounded text column.

    Args:
        max_length: Optional validation limit, not enforced by the database.
        **options: Options forwarded to `BaseField`.
    """

    column_type = Text
    input_type = "textarea"

    def __init__(self, max_length: int | None = None, **options: Any) -> None:
        """
        Store the optional validation limit.
        """
        self.max_length = max_length

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add a length validator when a limit was given.
        """
        if self.max_length is None:
            return []

        return [MaxLengthValidator(self.max_length)]

    def to_python(self, value: Any) -> str | None:
        """
        Convert the value to a string.
        """
        return None if value is None else str(value)

    def collect_attrs(self) -> dict[str, Any]:
        """
        Add the length attribute when limited.
        """
        attrs = super().collect_attrs()

        if self.max_length is not None:
            attrs["maxlength"] = self.max_length

        # Return the final attributes
        return attrs


class EmailField(CharField):
    """
    Text column validated as an email address.
    """

    default_max_length = 254
    input_type = "email"

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add email validation.
        """
        return [*super().get_default_validators(), EmailValidator()]


class URLField(CharField):
    """
    Text column validated as a URL.
    """

    default_max_length = 200
    input_type = "url"

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add URL validation.
        """
        return [*super().get_default_validators(), URLValidator()]


class SlugField(CharField):
    """
    Indexed text column validated as a URL slug.
    """

    default_max_length = 50

    def __init__(self, max_length: int | None = None, **options: Any) -> None:
        """
        Index slugs by default since they are used for lookups.
        """
        options.setdefault("index", True)

        # Pass the remaining options to the base field
        super().__init__(max_length, **options)

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add slug validation.
        """
        return [*super().get_default_validators(), SlugValidator()]


class GenericIPAddressField(CharField):
    """
    Text column validated as an IPv4 or IPv6 address.

    Args:
        protocol: One of "ipv4", "ipv6" or "both".
        **options: Options forwarded to `CharField`.
    """

    default_max_length = 45

    def __init__(self, protocol: str = "both", **options: Any) -> None:
        """
        Validate and store the protocol.
        """
        protocol = protocol.lower()

        if protocol not in IP_PARSERS:
            raise ValueError(f"protocol must be one of {sorted(IP_PARSERS)}.")

        # Store the protocol for later use in validators and input attributes
        self.protocol = protocol

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_default_validators(self) -> list[Callable[[Any], None]]:
        """
        Add address validation for the chosen protocol.
        """
        return [*super().get_default_validators(), IPAddressValidator(self.protocol)]


class TemporalField(BaseField):
    """
    Base class for date and time columns with automatic timestamps.

    Args:
        auto_now: Refresh the value on every update.
        auto_now_add: Set the value when the row is created.
        **options: Options forwarded to `BaseField`.
    """

    now_factory: ClassVar[Callable[[], Any]]

    def __init__(
        self,
        auto_now: bool = False,
        auto_now_add: bool = False,
        **options: Any,
    ) -> None:
        """
        Wire the automatic timestamp behaviour.
        """
        if auto_now or auto_now_add:
            options.setdefault("blank", True)
            options.setdefault("editable", False)
            options.setdefault("default", self.now_factory)

        if auto_now:
            options["onupdate"] = self.now_factory

        # Pass the remaining options to the base field
        super().__init__(**options)


class DateField(TemporalField):
    """
    Date column.
    """

    column_type = Date
    input_type = "date"
    now_factory = staticmethod(date.today)

    def to_python(self, value: Any) -> date | None:
        """
        Convert datetimes and ISO strings to a date.
        """
        if isinstance(value, datetime):
            return value.date()

        if value is None or isinstance(value, date):
            return value

        return self.parse(date.fromisoformat, value)


class DateTimeField(TemporalField):
    """
    Timezone-aware datetime column.
    """

    column_type = DateTime(timezone=True)
    input_type = "datetime-local"
    now_factory = staticmethod(utcnow)

    def to_python(self, value: Any) -> datetime | None:
        """
        Convert dates and ISO strings to a datetime.
        """
        if isinstance(value, datetime) or value is None:
            return value

        if isinstance(value, date):
            return datetime.combine(value, time.min)

        return self.parse(datetime.fromisoformat, value)


class TimeField(TemporalField):
    """
    Time of day column.
    """

    column_type = Time
    input_type = "time"
    now_factory = staticmethod(current_time)

    def to_python(self, value: Any) -> time | None:
        """
        Convert ISO strings to a time.
        """
        if value is None or isinstance(value, time):
            return value

        return self.parse(time.fromisoformat, value)


class DurationField(BaseField):
    """
    Time span column.
    """

    column_type = Interval

    def to_python(self, value: Any) -> timedelta | None:
        """
        Convert a number of seconds to a timedelta.
        """
        if value is None or isinstance(value, timedelta):
            return value

        return self.parse(lambda raw: timedelta(seconds=float(raw)), value)


class UUIDField(BaseField):
    """
    UUID column, stored natively where the database supports it.
    """

    column_type = Uuid

    def to_python(self, value: Any) -> uuid.UUID | None:
        """
        Convert strings to a UUID.
        """
        if value is None or isinstance(value, uuid.UUID):
            return value

        return self.parse(lambda raw: uuid.UUID(str(raw)), value)


class BinaryField(BaseField):
    """
    Raw bytes column, not editable in forms by default.
    """

    column_type = LargeBinary
    input_type = "file"

    def __init__(self, **options: Any) -> None:
        """
        Hide binary data from forms unless asked otherwise.
        """
        options.setdefault("editable", False)

        # Pass the remaining options to the base field
        super().__init__(**options)

    def to_python(self, value: Any) -> bytes | None:
        """
        Convert bytes-like objects and strings to bytes.
        """
        if value is None or isinstance(value, bytes):
            return value

        if isinstance(value, str):
            return value.encode()

        return self.parse(bytes, value)


class JSONField(BaseField):
    """
    JSON column holding any serialisable Python value.
    """

    column_type = JSON
    input_type = "textarea"

    def validate(self, value: Any) -> None:
        """
        Ensure the value can be serialised to JSON.
        """
        super().validate(value)

        try:
            json.dumps(value)
        except (TypeError, ValueError):
            self.fail("invalid")


class FileField(CharField):
    """
    Column storing the name of an uploaded file.

    Args:
        upload_to: Directory template using strftime codes, or a callable `(instance, filename) -> path`.
        storage: Storage backend, a `LocalStorage` under ./media by default.
        max_size: Largest accepted upload in bytes.
        allowed_extensions: Accepted extensions, with or without the dot.
        unique_names: Append a random suffix to avoid name collisions.
        **options: Options forwarded to `CharField`.
    """

    input_type = "file"

    # Configuration for unique file names
    UNIQUE_SUFFIX_LENGTH: ClassVar[int] = 8

    # Default error messages for file validation
    default_messages: ClassVar[dict[str, str]] = {
        "invalid_extension": "File extension {extension!r} is not allowed.",
        "file_too_large": "File exceeds the maximum size of {max_size} bytes.",
    }

    def __init__(
        self,
        upload_to: str = "",
        storage: StorageBackend | None = None,
        max_size: int | None = None,
        allowed_extensions: Sequence[str] | None = None,
        unique_names: bool = True,
        **options: Any,
    ) -> None:
        """
        Store the upload configuration.
        """
        self.upload_to = upload_to
        self.storage = storage
        self.max_size = max_size
        self.unique_names = unique_names
        self.allowed_extensions = {
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in allowed_extensions or ()
        }

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_storage(self) -> StorageBackend:
        """
        Return the configured storage backend, creating the default on first use.
        """
        from duck.settings.loaded import get_storage_backend

        if self.storage is None:
            self.storage = get_storage_backend("mediafiles")

        return self.storage # type: ignore

    def validate_upload(self, filename: str, size: int) -> None:
        """
        Check an upload against the extension and size limits.

        Args:
            filename: Original upload name.
            size: Upload size in bytes.

        Raises:
            ValidationError: If the upload is not acceptable.
        """
        extension = PurePosixPath(filename).suffix.lower()

        if self.allowed_extensions and extension not in self.allowed_extensions:
            self.fail("invalid_extension", extension=extension)

        if self.max_size is not None and size > self.max_size:
            self.fail("file_too_large", max_size=self.max_size)

    def save_file(
        self,
        filename: str,
        content: bytes,
        on_progress: ProgressCallback | None = None,
    ):
        """
        Validate and store an upload.

        Args:
            instance: Model instance the file belongs to.
            filename: Original upload name.
            content: Raw file bytes.
            on_progress: Optional callback for upload progress.
        """
        self.validate_upload(filename, len(content))

        # Determine the save function
        if self.unique_names:
            save_func = self.get_storage().save
        else:
            save_func = self.get_storage().save_as

        return save_func(
            data=content,
            filename=filename,
            folder=self.upload_to,
            on_progress=on_progress
        )

    async def async_save_file(
        self,
        filename: str,
        content: bytes,
        on_progress: ProgressCallback | None = None,
    ):
        """
        Validate and store an upload.

        Args:
            instance: Model instance the file belongs to.
            filename: Original upload name.
            content: Raw file bytes.

        Returns:
            The StoredFile object representing the saved file.
        """
        self.validate_upload(filename, len(content))

        # Determine the save func
        if self.unique_names:
            save_func = self.get_storage().async_save
        else:
            save_func = self.get_storage().async_save_as

        return await save_func(
            data=content,
            filename=filename,
            folder=self.upload_to,
            on_progress=on_progress
        )

    def delete_file(self, name: str) -> None:
        """
        Remove a stored file.
        """
        self.get_storage().delete(name)

    async def async_delete_file(self, name: str) -> None:
        """
        Remove a stored file.
        """
        await self.get_storage().async_delete(name)

    def url(self, name: str) -> str:
        """
        Return the public URL of a stored file.
        """
        return self.get_storage().url_for(name)

    def collect_attrs(self) -> dict[str, Any]:
        """
        Restrict the file picker to the allowed extensions.
        """
        attrs = super().collect_attrs()

        # Remove the maxlength attribute since it is not relevant for file inputs
        attrs.pop("maxlength", None)

        if self.allowed_extensions:
            attrs["accept"] = ",".join(sorted(self.allowed_extensions))

        return attrs


class ImageField(FileField):
    """
    File column restricted to common image extensions.
    """

    def __init__(self, **options: Any) -> None:
        """
        Default the allowed extensions to image formats.
        """
        options.setdefault("allowed_extensions", IMAGE_EXTENSIONS)

        # Pass the remaining options to the base field
        super().__init__(**options)


class FilePathField(CharField):
    """
    Column storing a path chosen from the local filesystem.

    Args:
        path: Directory to list.
        match: Regular expression file names must match.
        recursive: Whether to include subdirectories.
        allow_files: Whether files are valid choices.
        allow_folders: Whether folders are valid choices.
        **options: Options forwarded to `CharField`.
    """

    default_max_length = 100

    def __init__(
        self,
        path: str | Path,
        match: str | None = None,
        recursive: bool = False,
        allow_files: bool = True,
        allow_folders: bool = False,
        **options: Any,
    ) -> None:
        """
        Store the listing configuration.
        """
        self.path = Path(path)
        self.match = match
        self.recursive = recursive
        self.allow_files = allow_files
        self.allow_folders = allow_folders

        # Pass the remaining options to the base field
        super().__init__(**options)

    def get_choices(self) -> list[tuple[Any, str]]:
        """
        List the matching paths under the configured directory.
        """
        pattern = re.compile(self.match) if self.match else None
        entries = self.path.rglob("*") if self.recursive else self.path.glob("*")
        choices: list[tuple[Any, str]] = []

        for entry in sorted(entries):
            allowed = (entry.is_file() and self.allow_files) or (
                entry.is_dir() and self.allow_folders
            )

            if allowed and (pattern is None or pattern.search(entry.name)):
                choices.append((str(entry), str(entry.relative_to(self.path))))

        return choices


class ForeignKey(BaseField):
    """
    Column referencing another table.

    Args:
        to:
            Target model class, or a "table.column" or table name string.

        on_delete:
            Database action on delete: CASCADE, RESTRICT, SET NULL,
            SET DEFAULT or NO ACTION. Django names such as PROTECT,
            SET_NULL and DO_NOTHING are accepted too.

        to_field:
            Target column when `to` has no column part.

        **options:
            Options forwarded to `BaseField`.
    """

    input_type = "select"

    # Define the supported on_delete actions and their aliases
    ON_DELETE_ACTIONS: ClassVar[frozenset[str]] = frozenset(
        {"CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT", "NO ACTION"}
    )
    ON_DELETE_ALIASES: ClassVar[dict[str, str]] = {
        "PROTECT": "RESTRICT",
        "DO NOTHING": "NO ACTION",
    }

    def __init__(self, to: Any, on_delete: str = "CASCADE", to_field: str = "id", **options: Any) -> None:
        """
        Store the reference configuration.
        """

        # Default to an index since foreign keys are often used for lookups
        options.setdefault("index", True)

        # Store the reference configuration for later use in column creation and validation
        self.to = to
        self.to_field = to_field
        self.on_delete = self.normalize_on_delete(on_delete)

        # Pass the remaining options to the base field
        super().__init__(**options)

    @classmethod
    def normalize_on_delete(cls, action: str) -> str:
        """
        Convert an action name to its SQL form.

        Args:
            action: Action name such as "SET_NULL" or "CASCADE".

        Returns:
            The SQL action, e.g. "SET NULL".

        Raises:
            ValueError: If the action is not supported.
        """
        normalized = action.upper().replace("_", " ")
        normalized = cls.ON_DELETE_ALIASES.get(normalized, normalized)

        if normalized not in cls.ON_DELETE_ACTIONS:
            raise ValueError(f"Unsupported on_delete action: {action!r}.")

        return normalized

    def get_target(self) -> str:
        """
        Return the referenced "table.column" string.
        """
        if isinstance(self.to, str) and "." in self.to:
            return self.to

        # If the target is a model class, use its table name; otherwise assume it's a table name string
        table = self.to if isinstance(self.to, str) else self.to.__tablename__

        # If the target table is the same as the current table, use the primary key column
        return f"{table}.{self.to_field}"

    def get_column_args(self, name: str) -> list[Any]:
        """
        Add the foreign key constraint, which also infers the column type.
        """
        args = super().get_column_args(name)
        args.append(SAForeignKey(self.get_target(), ondelete=self.on_delete))

        # Return the positional arguments for the column, including the foreign key constraint
        return args


class OneToOneField(ForeignKey):
    """
    Foreign key that may be referenced by at most one row.
    """

    def __init__(self, to: Any, **options: Any) -> None:
        """
        Make the reference unique.
        """
        options.setdefault("unique", True)

        # Pass the remaining options to the base field
        super().__init__(to, **options)


class ManyToManyField(BaseField):
    """
    Many-to-many relationship backed by an association table.

    The target model must already be defined, and self-referential links
    are not supported.

    Args:
        to: Target model class.
        through: Association table name, derived from the model by default.
        related_name: Attribute added to the target for the reverse side.
        lazy: SQLAlchemy loading strategy, "selectin" works well with async.
        **options: Options forwarded to `BaseField`.
    """

    is_column = False
    input_type = "select"

    def __init__(
        self,
        to: type,
        through: str | None = None,
        related_name: str | None = None,
        lazy: str = "selectin",
        **options: Any,
    ) -> None:
        """
        Store the relationship configuration.
        """
        # Default to an optional field since the association table may be empty
        options.setdefault("blank", True)

        # Store the relationship configuration for later use in association table creation and relationship setup
        self.to = to
        self.through = through
        self.related_name = related_name
        self.lazy = lazy or "selectin"

        # Pass the remaining options to the base field
        super().__init__(**options)

    def contribute(self, owner: type, name: str) -> dict[str, Any]:
        """
        Create the association table and the relationship attribute.

        Args:
            owner: Model class being created.
            name: Attribute name the field is bound to.

        Returns:
            A mapping holding the relationship under the field name.
        """
        owner_table = owner.__tablename__
        target_table = self.to.__tablename__

        if owner_table == target_table:
            raise ValueError("Self-referential ManyToManyField is not supported.")

        # Find the primary key column names on both sides
        owner_pk = next(
            (f.db_column or key for key, f in owner.fields.items() if f.primary_key),
            "id",
        )

        # Find the primary key column name on the target side, defaulting to "id" if not found
        target_pk = next(iter(self.to.__table__.primary_key.columns)).name

        # Build the association table, rows vanish with either parent
        table = Table(
            self.through or f"{owner_table}_{name}",
            owner.metadata,
            Column(
                f"{owner_table}_{owner_pk}",
                SAForeignKey(f"{owner_table}.{owner_pk}", ondelete="CASCADE"),
                primary_key=True,
            ),
            Column(
                f"{target_table}_{target_pk}",
                SAForeignKey(f"{target_table}.{target_pk}", ondelete="CASCADE"),
                primary_key=True,
            ),
        )

        return {
            name: relationship(
                self.to,
                secondary=table,
                backref=self.related_name,
                lazy=self.lazy
            )
        }
