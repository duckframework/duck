"""
Declarative base model for Duck's SQLAlchemy database layer.
"""

import re

from collections.abc import Iterable
from typing import Any, ClassVar

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

from duck.db.fields import AutoField, BaseField, ValidationError
from duck.utils.string import to_snake_case, pluralize


# Stable constraint names keep Alembic migrations deterministic
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Error constant for non-field errors
NON_FIELD_ERRORS = "__all__"


class BaseModel(DeclarativeBase):
    """
    Base class for all Duck models.

    Declare `fields` on subclasses and they are compiled into SQLAlchemy
    columns automatically. The table name defaults to the pluralised snake
    case class name, and an auto-incrementing `id` primary key is added
    when none is declared. Mark a class with `__abstract__ = True` to share
    fields between models without creating a table.

    Example:

    ```python
    from duck.db import models

    class Event(BaseModel):
        title = models.CharField(max_length=120, help_text="Public event name")
        starts_at = models.DateTimeField()
        poster = models.ImageField(upload_to="posters/", blank=True)
    ```
    Attributes:
        fields: Mapping of attribute names to the field definitions.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    fields: ClassVar[dict[str, BaseField]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Compile declared fields into columns before SQLAlchemy maps the class.

        Args:
            **kwargs: Options forwarded to SQLAlchemy's declarative setup.
        """
        inherited, pending = cls.collect_fields()

        # Abstract models only record their fields for subclasses to reuse
        if vars(cls).get("__abstract__", False):
            cls.fields = {**inherited, **pending}

            # Forward the kwargs to SQLAlchemy so it can handle abstract models
            super().__init_subclass__(**kwargs)

            # Skip the rest of the setup for abstract models
            return

        # Add an automatic primary key when none was declared
        if not any(f.primary_key for f in {**inherited, **pending}.values()):
            pending = {"id": AutoField(), **pending}

        # Merge inherited and pending fields into a single mapping for this class
        cls.fields = {**inherited, **pending}

        # Derive the table name unless one is set or inherited
        if not inherited and not {"__tablename__", "__table__"} & vars(cls).keys():
            cls.__tablename__ = pluralize(to_snake_case(cls.__name__))

        # Replace declared fields with SQLAlchemy columns and relationships
        for name, field in pending.items():
            for attr, value in field.contribute(cls, name).items():
                setattr(cls, attr, value)

        # Forward the kwargs to SQLAlchemy so it can handle the new columns
        super().__init_subclass__(**kwargs)

    @classmethod
    def collect_fields(cls,) -> tuple[dict[str, BaseField], dict[str, BaseField]]:
        """
        Gather declared fields from the class hierarchy.

        Returns:
            A tuple of (inherited, pending). Inherited fields are already
            mapped by a concrete parent, while pending fields still need
            columns on this class.
        """
        inherited: dict[str, BaseField] = {}
        pending: dict[str, BaseField] = {}

        # Walk bases first so subclasses override parent declarations
        for klass in reversed(cls.__mro__):
            namespace = vars(klass)

            if "__table__" in namespace:
                inherited.update(namespace.get("fields", {}))
                continue

            for name, value in namespace.items():
                if isinstance(value, BaseField):
                    pending[name] = value

        return inherited, pending

    @classmethod
    def describe_fields(cls, editable_only: bool = True) -> list[dict[str, Any]]:
        """
        Describe the model's fields for forms and other UI code.

        Args:
            editable_only: Skip fields marked as not editable.

        Returns:
            One description dictionary per field, in declaration order.
        """
        return [
            field.describe(name)
            for name, field in cls.fields.items()
            if field.editable or not editable_only
        ]

    def to_dict(self, exclude: Iterable[str] = ()) -> dict[str, Any]:
        """
        Return the column values as a dictionary.

        Args:
            exclude: Attribute names to leave out.

        Returns:
            A mapping of attribute names to current values.
        """
        return {
            name: getattr(self, name)
            for name, field in self.fields.items()
            if field.is_column and name not in exclude
        }

    def clean(self) -> None:
        """
        Hook for model-wide validation, override in subclasses.

        Raises:
            ValidationError: If the instance is invalid as a whole.
        """

    def clean_fields(self, exclude: Iterable[str] = ()) -> None:
        """
        Validate and convert every column value.

        Args:
            exclude: Attribute names to skip.

        Raises:
            ValidationError: Mapping field names to their error messages.
        """
        errors: dict[str, list[str]] = {}

        for name, field in self.fields.items():
            if not field.is_column or name in exclude:
                continue

            value = getattr(self, name, None)

            # Defaults are applied on flush, so missing values are fine
            if value is None and field.has_default:
                continue

            try:
                setattr(self, name, field.clean(value))
            except ValidationError as exc:
                errors[name] = exc.messages

        if errors:
            raise ValidationError(errors)

    def full_clean(self, exclude: Iterable[str] = ()) -> None:
        """
        Run field validation followed by the model-wide `clean` hook.

        Args:
            exclude: Attribute names to skip during field validation.

        Raises:
            ValidationError: Mapping field names to their error messages.
        """
        errors: dict[str, list[str]] = {}

        # Field-level errors first
        try:
            self.clean_fields(exclude)
        except ValidationError as exc:
            errors.update(exc.detail)

        # Then errors that concern the whole instance
        try:
            self.clean()
        except ValidationError as exc:
            errors.setdefault(NON_FIELD_ERRORS, []).extend(exc.messages)

        if errors:
            raise ValidationError(errors)

    def save(self, session: Session, validate: bool = True, commit: bool = True) -> "BaseModel":
        """
        Insert or update the instance.

        Create the session with `expire_on_commit=False` so attributes stay
        readable after the commit in async code.

        Args:
            session: Active async session.
            validate: Run `full_clean` before saving.
            commit: Commit the transaction, otherwise only flush.

        Returns:
            The saved instance.

        Raises:
            ValidationError: If validation is enabled and fails.
        """
        if validate:
            self.full_clean()

        # Persist the instance
        session.add(self)

        # Flush to generate any defaults and validate constraints before committing
        session.flush()

        if commit:
            session.commit()

        return self
    
    async def async_save(self, session: AsyncSession, validate: bool = True, commit: bool = True) -> "BaseModel":
        """
        Insert or update the instance.

        Create the session with `expire_on_commit=False` so attributes stay
        readable after the commit in async code.

        Args:
            session: Active async session.
            validate: Run `full_clean` before saving.
            commit: Commit the transaction, otherwise only flush.

        Returns:
            The saved instance.

        Raises:
            ValidationError: If validation is enabled and fails.
        """
        if validate:
            self.full_clean()

        # Persist the instance
        session.add(self)

        # Flush to generate any defaults and validate constraints before committing
        await session.flush()

        if commit:
            await session.commit()

        return self

    def delete(self, session: Session, commit: bool = True) -> None:
        """
        Delete the instance.

        Args:
            session: Active session.
            commit: Commit the transaction, otherwise only flush.
        """
        session.delete(self)
        session.flush()

        if commit:
            session.commit()
        
    async def async_delete(self, session: AsyncSession, commit: bool = True) -> None:
        """
        Delete the instance.

        Args:
            session: Active async session.
            commit: Commit the transaction, otherwise only flush.
        """
        await session.delete(self)
        await session.flush()

        if commit:
            await session.commit()

    def __repr__(self) -> str:
        """
        Show the class name and primary key values.
        """
        keys = ", ".join(
            f"{name}={getattr(self, name, None)!r}"
            for name, field in self.fields.items()
            if field.primary_key
        )

        return f"<{type(self).__name__} {keys}>"


class Model(BaseModel):
    """
    Base class for all concrete Duck models.

    This class is provided for convenience, but you can subclass `BaseModel`
    directly if you prefer.
    """

