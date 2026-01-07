"""
API for freezing components.
"""
from typing import (
    Any,
    Mapping,
    Optional,
    Iterable,
    Tuple,
    List,
    Type,
)
from collections.abc import (
    MutableMapping,
    MutableSequence,
)

from duck.html.components.extensions import Extension
from duck.html.components.core.exceptions import HtmlComponentError as ComponentError
from duck.utils.threading.threadpool import get_or_create_thread_manager


class FrozenComponentError(ComponentError):
    """
    Raised on attempts to mutate frozen components or data.
    """
    pass


class FreezeableComponentError(ComponentError):
    """
    Raised on freezeable components when a certain action fails.
    """


class FrozenDataType:
    """
    Base class to prevent mutation.
    """
    __slots__ = ()
    
    def __getattribute__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError as e:
            raise AttributeError(
                f"{e}. The reason may be because the component with this data has been frozen somehow."
            )
            
    def __setattr__(self, key, value):
        raise FrozenComponentError(f"Cannot set attribute '{key}' on frozen object.")
         
    def __delattr__(self, key):
        raise FrozenComponentError(f"Cannot delete attribute '{key}' on frozen object.")
         
    def __setitem__(self, key, value):
        raise FrozenComponentError(f"Cannot set item '{key}' on frozen object.")
         
    def __delitem__(self, key):
        raise FrozenComponentError(f"Cannot delete item '{key}' on frozen object.")
        
    def __repr__(self):
        data = super().__repr__()
        return f"<{self.__class__.__name__} {data}>"
        
    __str__ = __repr__


class FrozenTuple(FrozenDataType, tuple):
    __slots__ = ()
    

class FrozenDict(FrozenDataType, dict):
    __slots__ = ("_version", "_hash")
    
    def __init__(self, mapping: Optional[Mapping] = None):
        super().__init__(mapping)
        mapping = mapping or {}
        
        # Maybe this mapping is a PropertyStore or StyleStore, lets copy the _version attr (if available)
        version = getattr(mapping, "_version", None)
        if version is not None:
            object.__setattr__(self, "_version", version)
        
    def __hash__(self):
        _hash = object.__getattribute__(self, "_hash", None)
        if not _hash:
            _hash = hash(frozenset(self.items()))
            object.__setattr__(self, "_hash", _hash)
        return _hash    


def do_freeze(
    value: Any,
    responsible_component: Optional["HtmlComponent"] = None,
    exceptional_components: Optional[List["HtmlComponent"]] = None,
    exceptional_types: Optional[List[Type]] = None,
) -> Any:
    """
    Convert arbitrary values into deeply immutable equivalents (iterative, cycle-safe).

    Rules:
    - Immutable primitives are returned as-is
    - Tuple/List/MutableSequence -> FrozenTuple
    - Dict/Mapping -> FrozenDict
    - Set -> frozenset
    - Objects exposing `freeze()` -> call freeze()
    - Other custom objects raise ComponentError
    """
    # Normalize inputs
    exceptional_components = set(exceptional_components or ())
    exceptional_types = tuple(exceptional_types) if exceptional_types else None

    # Fast locals
    IMMUTABLE_PRIMITIVES = (str, int, float, bytes, bool, type(None))
    id_ = id
    isinstance_ = isinstance

    # Memo table (cycle-safe)
    memo = {}

    # Stack machine states
    ENTER, EXIT = 0, 1
    stack = [(ENTER, value, None)]
    result = None

    while stack:
        state, current, parent = stack.pop()
        obj_id = id_(current)

        # -------------------------------
        # EXIT phase
        # -------------------------------
        if state == EXIT:
            frozen = memo[obj_id]

            # Finalize sequence
            if isinstance_(frozen, list):
                frozen = FrozenTuple(frozen)

            # Finalize mapping
            elif isinstance_(frozen, dict):
                # Collapse value cells
                for k, cell in frozen.items():
                    frozen[k] = cell[0]

                frozen = FrozenDict(frozen)

                version = getattr(current, "_version", None)
                if version is not None:
                    object.__setattr__(frozen, "_version", version)

            # Finalize set
            elif isinstance_(frozen, set):
                frozen = frozenset(frozen)

            memo[obj_id] = frozen

            # Attach to parent
            if parent is not None:
                # Dict value cell
                if (
                    isinstance_(parent, list)
                    and len(parent) == 1
                    and parent[0] is None
                ):
                    parent[0] = frozen
                else:
                    parent.append(frozen)
            else:
                result = frozen

            continue

        # -------------------------------
        # ENTER phase
        # -------------------------------
        try:
            if current in exceptional_components:
                frozen = current
                memo[obj_id] = frozen

                if parent is not None:
                    if (
                        isinstance_(parent, list)
                        and len(parent) == 1
                        and parent[0] is None
                    ):
                        parent[0] = frozen
                    else:
                        parent.append(frozen)
                else:
                    result = frozen
                continue
        except TypeError:
            pass

        if exceptional_types and isinstance_(current, exceptional_types):
            frozen = current

        elif isinstance_(current, IMMUTABLE_PRIMITIVES):
            frozen = current

        elif obj_id in memo:
            frozen = memo[obj_id]

        # Sequence
        elif isinstance_(current, (tuple, list, MutableSequence)):
            temp = []
            memo[obj_id] = temp
            stack.append((EXIT, current, parent))
            for v in reversed(current):
                stack.append((ENTER, v, temp))
            continue

        # Mapping
        elif isinstance_(current, (dict, Mapping)):
            temp = {}
            memo[obj_id] = temp
            stack.append((EXIT, current, parent))

            for k, v in reversed(list(current.items())):
                cell = [None]
                temp[k] = cell
                stack.append((ENTER, v, cell))
            continue

        # Set
        elif isinstance_(current, set):
            temp = set()
            memo[obj_id] = temp
            stack.append((EXIT, current, parent))
            for v in current:
                stack.append((ENTER, v, temp))
            continue

        # Custom freeze hook
        elif hasattr(current, "freeze") and callable(current.freeze):
            try:
                frozen = current.freeze(
                    responsible_component=responsible_component,
                    exceptional_components=list(exceptional_components),
                    exceptional_types=exceptional_types,
                )
            except Exception as exc:
                raise FreezeableComponentError(
                    f"Error while freezing object of type {type(current).__name__}: {exc}."
                ) from exc

        else:
            raise ComponentError(
                f"Cannot freeze object of type {type(current).__name__}. "
                f"Object must implement method 'freeze'"
            )

        memo[obj_id] = frozen

        if parent is not None:
            if (
                isinstance_(parent, list)
                and len(parent) == 1
                and parent[0] is None
            ):
                parent[0] = frozen
            else:
                parent.append(frozen)
        else:
            result = frozen
    return result


class FreezeableComponent(Extension):
    """
    A component extension providing deep immutability similar to Python tuples.

    After calling `.freeze(responsible_component)`:
    - Instance attributes are replaced with deeply frozen equivalents
    - Child components (if any) are recursively frozen
    - Further attribute set/delete operations will raise FreezeableComponentError
    
    Benefits:
    - Frozen components cache their entire rendered output or vdom as compared to ordinary components. This 
          may drastically improve component rendering by `>= 100%` (same as VDOM creation).
    - Benefits of frozen components are only realized on subsequent actions like `render` or `to_vdom`. The initial `render` or `to_vdom` will 
          will be a little bit slower than normal components (by very few milliseconds) but subsequent calls will result in instant execution (typically <= 1ms or more depending on component).
    - This protects static components from unnecessary changes or alterations.
    - etc
    
    Notes:
    - Only freeze static components that doesn't require further changes or modifications.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize extension state. Subclasses' __init__ run after Extension.__init__
        and before freeze is performed.
        """
        self.__is_frozen: bool = False
        self._freeze_exception_id = None
        self._freeze_in_progress = False
        self._freeze_responsible_component: Optional[Any] = None
        self._temp_partial_unfreeze_ctx_manager = None
        self._initially_frozen = False # Used by the temp partial unfreeze context manager
        super().__init__(*args, **kwargs)
        
        # This will set the exception_key for frozen components so that copied components will render well
        self._freeze_exception_key()
        
        # These are attributes to disallow modification even if we are inside temp_partial_unfreeze context manager
        self._temp_partial_unfreeze_disallow_attrs = [
            "_HtmlComponent__inner_html",
            "_HtmlComponent__properties",
            "_HtmlComponent__style",
            "_InnerHtmlComponent__children",
        ]
        
        # Exceptional components to skip freeze
        self._component_freeze_exceptions = None
        self._component_freeze_exception_types = None
        self._is_component_freeze_exception = False # Will be set by freeze if self in exceptional_components
        
        # Allow passing extra names to exclude from freezing (common caches, etc.)
        exceptions = kwargs.get("freeze_exceptions", ())
        
        # Use list in cases where user wants to directly alter exceptions.
        self._freeze_exceptions: List[str, ...] = list(
            [
                "_domcontentloaded_event_called",
                "_event_bindings_changed",
                "_freeze_exceptions",
                "_freeze_exception_id",
                "__is_frozen",
                "_freezing_in_progress",
                "_initially_frozen",
                "_prev_states",
                "_is_from_cache",
                "_temp_partial_unfreeze_ctx_manager",
                "_is_component_freeze_exception",
                "_component_freeze_exceptions",
                "_component_freeze_exception_types",   
            ]
            + list(exceptions)
        )
        
    def freeze_in_progress(self) -> bool:
        """
        Returns a boolean on whether if freezing is in progress.
        """
        return self._freeze_in_progress
        
    def pre_render(self):
        # Pre-render compatible with frozen components
        if self.is_frozen():
            with self.temp_partial_unfreeze(unfreeze_descendants=True):
                return super().pre_render()
        else:
            return super().pre_render()
            
    def render(self):
        """       
        Return cached rendered output when frozen, otherwise call parent's render.
        If frozen and no cached value exists, compute, cache, and return it.
        """
        # Exceptional components are not yet supported, the implementation will be completed in the future.
        output = None
        
        if self.is_frozen():
            cached = self._cached_rendered_output
            if cached is not None:
                return cached
            else:
                with self.temp_partial_unfreeze(unfreeze_descendants=True):
                    output = super().render()
        else:
            output = super().render()
        return output
        
    def to_vdom(self):
        """
        Returns cached vdom if frozen else it's recomputed.
        """
        vdom = None
        
        if self.is_frozen():
            cached = self._cached_vdom_node
            if cached is not None:
                return cached
            else:
                with self.temp_partial_unfreeze(unfreeze_descendants=True):
                    vdom = super().to_vdom()
        else:
            vdom = super().to_vdom()
        
        # Return final vdom
        return vdom
     
    def temp_partial_unfreeze(
        self,
        custom_component: Optional['HtmlComponent'] = None,
        unfreeze_descendants: bool = False
    ):
        """
        Returns context manager for temporarily unfreeze component.
    
        ```{warning}
        Do not use this context manager unnecessarily as it unlocks free manipulation
        of attributes. Before using this, user must understand why the component was
        frozen in the first place. Using this without understanding why the component
        was frozen in the first place may remove performance benefits from frozen components.
        ```
    
        Args:
            custom_component (Optional[HtmlComponent]): Unfreeze temporarily for a custom
                component. Defaults to None to use current component.
            unfreeze_descendants (bool): Whether to unfreeze children or grand-children
                as well. Defaults to False.
    
        Notes:
        - Allows free manipulation of component attributes.
        - Frozen semantic state remains conceptually frozen.
        - This is intentionally low-level and unsafe if abused.
        """
        root = custom_component or self
    
        class TempPartialUnfreezeContextManager:
            """
            Context manager for temporary & partial component unfreeze.
            """
            __slots__ = ("_targets",)
    
            def __enter__(this):
                """
                Iteratively unfreeze target component (and optionally descendants).
                """
                stack = [root]
                targets = []  # Preserve traversal order for symmetric restore
    
                # Local bindings for performance
                get_children = getattr
                is_frozen = lambda c: c.is_frozen()
    
                while stack:
                    component = stack.pop()
                    targets.append(component)
    
                    original_is_frozen = is_frozen(component)
                    component._initially_frozen = original_is_frozen
    
                    if original_is_frozen:
                        component._unfrze(this)
                        assert not component.is_frozen(), (
                            "Error unfreezing component temporarily."
                        )
    
                    if unfreeze_descendants:
                        children = get_children(component, "children", ())
                        for child in children:
                            setattr(child, "_temp_partial_unfreeze_ctx_manager", this)
                            stack.append(child)
    
                this._targets = targets
                return this
    
            def __exit__(this, *exc):
                """
                Restore original freeze state iteratively in reverse order.
                """
                for component in reversed(this._targets):
                    if component._initially_frozen:
                        component._frze(this)
                        assert component.is_frozen(), (
                            "Error restoring component freeze state."
                        )
                return False
    
        # Context managers must never be reused
        ctx_manager = TempPartialUnfreezeContextManager()
        return ctx_manager
        
    def _unfrze(self, context_manager):
        # Set freeze state to False
        object.__setattr__(self, "__is_frozen", False)
         
    def _frze(self, context_manager):
        # Set freeze state to True'
        object.__setattr__(self, "__is_frozen", True)     
     
    def freeze(
        self,
        responsible_component: Optional["HtmlComponent"] = None,
        deep: bool = False,
        freeze_in_background: bool = True,
        **kwargs,
    ):
        """
        Freeze the component and its nested state.

        Args:
            responsible_component: Optional component that is responsible for freezing this one.
                if None, the component will mark itself as responsible.
            deep (bool): Whether to do deep freeze all component attributes. Defaults to False, this only targets important attributes like props, style and children.
            freeze_in_background (bool): Freezing may be heavy and slow, we do it in background. Defaults to True.
        """
        if freeze_in_background:
            worker = get_or_create_thread_manager("component-bg-worker", strictly_get=True)
            worker.submit_task(lambda: self._freeze(rssponsible_component, deep), task_type="component-task")
        else:
            self._freeze(responsible_component, deep)
            
    def _freeze(
        self,
        responsible_component: Optional["HtmlComponent"] = None,
        deep: bool = False,
        **kwargs,
    ):
        """
        Freeze the component and its nested state.

        Args:
            responsible_component: Optional component that is responsible for freezing this one.
                if None, the component will mark itself as responsible.
            deep (bool): Whether to do deep freeze all component attributes. Defaults to False, this only targets important attributes like props, style and children.
        """
        # TODO: Implement exceptional_components/exceptional_types, for now its causing problems in `render` method.
        exceptional_components = []
        exceptional_types = None
        
        if self.is_frozen():
            return
        
        # Update exceptional components
        self._component_freeze_exceptions = exceptional_components
        self._component_freeze_exception_types = exceptional_types
        
        for exc in exceptional_components:
            if not getattr(exc, "_is_component_freeze_exception", False):
                exc._is_component_freeze_exception = True
            
            if exc is self:
                # Do not freeze self but freeze children
                children = getattr(self, "children", [])
                if children:
                    do_freeze(
                        value=children,
                        responsible_component=responsible_component,
                        exceptional_components=exceptional_components,
                        exceptional_types=exceptional_types,
                    )
                return
                
        if exceptional_types and isinstance(self, tuple(exceptional_types)):
            if not getattr(self, "_is_component_freeze_exception", False):
                self._is_component_freeze_exception = True
            
            # Do not freeze self but freeze children
            children = getattr(self, "children", [])
            if children:
                do_freeze(
                    value=children,
                    responsible_component=responsible_component,
                    exceptional_components=exceptional_components,
                    exceptional_types=exceptional_types,
                )
            return
            
        # Check if component is loaded
        self.raise_if_not_loaded(
            f"Component {self} is not loaded. "
            f"This might mean that this is a lazy component."
        )
        
        # Freeze instance attributes (skip exceptions)
        # We iterate over a snapshot of keys to avoid mutation during iteration.
        attrs = list(self.__dict__.items()) if deep else ({"_HtmlComponent__properties": self.props, "_HtmlComponent__style": self.style, "_InnerHtmlComponent__children": getattr(self, "children", ())}).items()
        responsible_component = responsible_component or self
        
        for key, value in attrs:
            if not hasattr(self, key):
                continue
                
            elif key in self._freeze_exceptions:
                # keep as-is
                continue
            
            elif value is self:
                # Not doing this will cause recursion error
                continue
            
            try:
                # Don't worry, children are frozen here also.
                frozen_val = do_freeze(
                    value,
                    responsible_component=responsible_component,
                    exceptional_components=exceptional_components,
                    exceptional_types=exceptional_types,
                )
            except FreezeableComponentError:
                # If an attribute can't be frozen, raise — caller must handle.
                raise
            
            # set frozen value directly (bypass __setattr__ protection)
            super().__setattr__(key, frozen_val)
            
        # Set some attributes
        object.__setattr__(self, "__is_frozen", True)
        object.__setattr__(self, "_freeze_responsible_component", responsible_component)
        
    def ensure_freeze(self, *args, **kwargs):
        """
        This works just like `freeze()` but does not raise an exception if component is not yet loaded.  
        
        It ensures that `freeze` is called whenever the component is loaded (if not already loaded) or 
        just freeze the component right away if component is already loaded.
        """
        if self.is_frozen():
            return
        
        def ensure_freeze():
            """
            This just freezes the component and provide a reference for debugging 
            when `load()` fails because of this function. 
            """
            self.freeze(*args, **kwargs)
            
        if self.is_loaded():
            self.freeze(*args, **kwargs)
        else:
            # Load is not called yet or already loading.
            self._ensure_freeze_callback = ensure_freeze
             
            if self.is_loaded() and not self.is_frozen():
                # Component already loaded, maybe component was loading already 
                # but it was about to finish that it didn't see the _ensure_freeze_callback attribute.
                self.freeze(*args, **kwargs)
             
    def is_frozen(self) -> bool:
        """
        Returns whether this component is frozen.
        """
        return bool(getattr(self, "__is_frozen", False))
        
    def _is_freeze_exception(self) -> bool:
        """
        Returns a boolean on whether this is an exceptional component that was skipped 
        when freezing was done.
        """
        return (
            not self.is_frozen()
            and getattr(self, "_is_component_freeze_exception", False)
        )        
    
    def _freeze_exception_key(self) -> str:
        if not self._freeze_exception_id:
            self._freeze_exception_id = "freeze_exc_%s"%id(self)
        return self._freeze_exception_id
        
    # Mutation lockdown
    def __setattr__(self, key, value):
        """
        Block attribute assignment when frozen except for allowed exceptions.
        """
        freeze_exceptions = getattr(self, "_freeze_exceptions", ())
        
        if (
            self.is_frozen()
            and key not in freeze_exceptions
        ):
            responsible = getattr(self, "_freeze_responsible_component", None)
            if responsible and responsible is not self:
                detail = f" Responsible component: {responsible}."
            else:
                detail = ""
            raise FrozenComponentError(f"Cannot modify frozen component attribute '{key}' on {self}.{detail}")
       
        if getattr(self, "_initially_frozen", False) and key in self._temp_partial_unfreeze_disallow_attrs:
            # We are in temp_partial_unfreeze context manager
            responsible = getattr(self, "_freeze_responsible_component", None)
            if responsible and responsible is not self:
                detail = f" Responsible component: {responsible}."
            else:
                detail = ""
            raise FrozenComponentError(f"Attribute '{key}' of {self} is frozen permanently and cannot be modified.{detail}")
            
        super().__setattr__(key, value)

    def __delattr__(self, key):
        """
        Block attribute deletion when frozen except for allowed exceptions.
        """
        freeze_exceptions = getattr(self, "_freeze_exceptions", ())
        if self.is_frozen() and key not in freeze_exceptions:
            responsible = getattr(self, "_freeze_responsible_component", None)
            if responsible and responsible is not self:
                detail = f" Responsible component: {responsible}."
            else:
                detail = ""
            raise FrozenComponentError(f"Cannot delete attribute '{key}' on frozen component {self}.{detail}")
        
        if getattr(self, "_initially_frozen", False) and key in self._temp_partial_unfreeze_disallow_attrs:
            # We are in temp_partial_unfreeze context manager
            responsible = getattr(self, "_freeze_responsible_component", None)
            if responsible and responsible is not self:
                detail = f" Responsible component: {responsible}."
            else:
                detail = ""
            raise FrozenComponentError(f"Attribute '{key}' of {self} is frozen permanently and cannot be modified.{detail}")
            
        super().__delattr__(key)


# Create a familiar alias
FreezeableComponentExtension = FreezeableComponent
