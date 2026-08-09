"""
Decorators for authentication.
"""
import functools
import inspect

from typing import Callable, Optional, Union

from duck.contrib.sync import ensure_async, ensure_sync
from duck.contrib.auth.helpers import get_user_id, async_get_user_id, get_user, async_get_user
from duck.shortcuts import redirect, resolve
from duck.views import View


DEFAULT_LOGIN_URL: Optional[str] = None
DEFAULT_LOGIN_URL_RESOLVER: Optional[Callable] = None


def set_default_login_url(login_url: str) -> None:
    """
    Sets the fallback login_url used by login_required when a decorated
    view provides neither login_url nor login_url_resolver.

    Args:
        login_url: A fixed route name or path to redirect to.
    """
    global DEFAULT_LOGIN_URL, DEFAULT_LOGIN_URL_RESOLVER
    DEFAULT_LOGIN_URL = login_url
    DEFAULT_LOGIN_URL_RESOLVER = None


def set_default_login_url_resolver(login_url_resolver: Callable) -> None:
    """
    Sets the fallback login_url_resolver used by login_required when a
    decorated view provides neither login_url nor login_url_resolver.

    Args:
        login_url_resolver: A callable receiving the request and
            returning the redirect URL as a string.
    """
    global DEFAULT_LOGIN_URL, DEFAULT_LOGIN_URL_RESOLVER
    
    DEFAULT_LOGIN_URL_RESOLVER = login_url_resolver
    DEFAULT_LOGIN_URL = None


def login_required(
    view: Optional[Union[Callable, View]] = None,
    *,
    login_url: Optional[str] = None,
    login_url_resolver: Optional[Callable] = None,
):
    """
    Restricts a view or View.run method to authenticated users only.

    Wraps a Duck view so unauthenticated requests are redirected
    instead of reaching the handler. Works on plain view functions
    and on View.run methods alike, and supports both sync and async
    handlers.

    If neither login_url nor login_url_resolver is given, the values
    set via set_default_login_url/set_default_login_url_resolver are
    used instead. Exactly one source, explicit or default, must
    resolve for the decorator to know where to redirect.

    Args:
        view: The view function or View.run method being decorated.
            Left as None when the decorator is called with arguments,
            e.g. `@login_required(login_url="/login")`.

        login_url: A fixed route name or path to redirect to. Passed
            through resolve() first, falling back to the raw value
            if resolution fails (e.g. it's already a raw path).

        login_url_resolver: A callable receiving the request and
            returning the redirect URL as a string. Use this when the
            destination depends on request state, e.g. a next param.

    Returns:
        The decorated view, or a decorator awaiting the view if
        called with keyword arguments only.

    Raises:
        ValueError: If both login_url and login_url_resolver are
            given, or if neither is given and no default is set.
    """
    if login_url and login_url_resolver:
        raise ValueError("Decorator `login_required` accepts only one of login_url or login_url_resolver")

    # Fall back to module-level defaults when neither was provided
    if not login_url and not login_url_resolver:
        login_url = DEFAULT_LOGIN_URL
        login_url_resolver = DEFAULT_LOGIN_URL_RESOLVER

    if not login_url and not login_url_resolver:
        raise ValueError(
            "Decorator `login_required` requires login_url or login_url_resolver, "
            "or a default set via set_default_login_url/set_default_login_url_resolver"
        )

    def resolve_redirect_url(request) -> str:
        """
        Determines the redirect target for an unauthenticated request.
        """
        if login_url_resolver:
            return login_url_resolver(request)
        try:
            return resolve(login_url)
        except Exception:
            return login_url

    def decorator(fn: Callable) -> Callable:
        """
        Wraps fn with an authentication check, matching its calling
        convention (View.run method vs plain function) and sync/async
        nature.
        """
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(first_arg, *args, **kwargs):
                """
                Checks auth via async_get_user_id before delegating to fn.
                """
                # Detect calling convention: View.run method vs plain function
                if isinstance(first_arg, View):
                    view_obj = first_arg
                    request = args[0]
                else:
                    view_obj = None
                    request = first_arg

                # Lightweight check, only reads session/JWT, not the DB
                user_id = await async_get_user_id(request)
                if not user_id:
                    return redirect(resolve_redirect_url(request))

                if view_obj is not None:
                    return await fn(view_obj, request, **kwargs)
                return await fn(request, *args, **kwargs)
            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(first_arg, *args, **kwargs):
            """
            Checks auth via get_user_id before delegating to fn.
            """
            # Detect calling convention: View.run method vs plain function
            if isinstance(first_arg, View):
                view_obj = first_arg
                request = args[0]
            else:
                view_obj = None
                request = first_arg

            # Lightweight check, only reads session/JWT, not the DB
            user_id = get_user_id(request)
            if not user_id:
                return redirect(resolve_redirect_url(request))

            if view_obj is not None:
                return fn(view_obj, request, **kwargs)
            return fn(request, *args, **kwargs)
        return sync_wrapper

    # Support both @login_required and @login_required(login_url=...)
    if view is not None:
        return decorator(view)
    return decorator


def user_required(
    view: Optional[Union[Callable, View]] = None,
    *,
    login_url: Optional[str] = None,
    login_url_resolver: Optional[Callable] = None,
    **get_user_kwargs,
):
    """
    Restricts a view or View.run method to authenticated users only,
    resolving the full user model and attaching it to the request.

    Unlike login_required, which only checks that a user_id is
    present in the session/JWT, this decorator resolves the actual
    user model (a DB read) and sets `request.user` before calling the
    handler. Use this when the view body needs user fields, not just
    the fact that someone is logged in.

    Args:
        view: The view function or View.run method being decorated.
            Left as None when the decorator is called with arguments,
            e.g. `@user_required(login_url="/login")`.

        login_url: A fixed route name or path to redirect to. Passed
            through resolve() first, falling back to the raw value
            if resolution fails (e.g. it's already a raw path).

        login_url_resolver: A callable receiving the request and
            returning the redirect URL as a string. Use this when the
            destination depends on request state, e.g. a next param.

        **get_user_kwargs: Forwarded to get_user/async_get_user after
            request, e.g. select_related=[...] or a tenant scope.

    Returns:
        The decorated view, or a decorator awaiting the view if
        called with keyword arguments only.

    Raises:
        ValueError: If both login_url and login_url_resolver are
            given, or if neither is given and no default is set.
    """
    if login_url and login_url_resolver:
        raise ValueError("Decorator `user_required` accepts only one of login_url or login_url_resolver")

    # Fall back to module-level defaults when neither was provided
    if not login_url and not login_url_resolver:
        login_url = DEFAULT_LOGIN_URL
        login_url_resolver = DEFAULT_LOGIN_URL_RESOLVER

    if not login_url and not login_url_resolver:
        raise ValueError(
            "Decorator `user_required` requires login_url or login_url_resolver, "
            "or a default set via set_default_login_url/set_default_login_url_resolver"
        )

    def resolve_redirect_url(request) -> str:
        """
        Determines the redirect target for an unauthenticated request.
        """
        if login_url_resolver:
            return login_url_resolver(request)
        try:
            return resolve(login_url)
        except Exception:
            return login_url

    def decorator(fn: Callable) -> Callable:
        """
        Wraps fn with a full user-model resolution check, matching
        its calling convention (View.run method vs plain function)
        and sync/async nature.
        """
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(first_arg, *args, **kwargs):
                """
                Resolves the user model via async_get_user before
                delegating to fn.
                """
                # Detect calling convention: View.run method vs plain function
                if isinstance(first_arg, View):
                    view_obj = first_arg
                    request = args[0]
                else:
                    view_obj = None
                    request = first_arg

                # Full DB resolution, with caller-supplied kwargs forwarded through
                user = await async_get_user(request, **get_user_kwargs)
                
                if not user:
                    return redirect(resolve_redirect_url(request))

                # Assign user on request
                request.user = user

                if view_obj is not None:
                    return await fn(view_obj, request, **kwargs)
                return await fn(request, *args, **kwargs)
            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(first_arg, *args, **kwargs):
            """
            Resolves the user model via get_user before delegating
            to fn.
            """
            # Detect calling convention: View.run method vs plain function
            if isinstance(first_arg, View):
                view_obj = first_arg
                request = args[0]
            else:
                view_obj = None
                request = first_arg

            # Full DB resolution, with caller-supplied kwargs forwarded through
            user = get_user(request, **get_user_kwargs)
            
            if not user:
                return redirect(resolve_redirect_url(request))

            # Assign user
            request.user = user
            
            if view_obj is not None:
                return fn(view_obj, request, **kwargs)
            return fn(request, *args, **kwargs)
        return sync_wrapper

    # Support both @user_required and @user_required(login_url=...)
    if view is not None:
        return decorator(view)
    return decorator

def condition_required(
    condition: Callable[..., bool],
    view: Optional[Union[Callable, View]] = None,
    *,
    redirect_url: Optional[str] = None,
    redirect_url_resolver: Optional[Callable] = None,
    condition_args: Optional[tuple] = None,
    condition_kwargs: Optional[dict] = None,
):
    """
    Restricts a view or View.run method to requests matching a
    condition evaluated against the request object.

    Generalizes login_required/user_required into an arbitrary
    predicate, e.g. request.user.is_staff or request.headers.get(...).
    Use a plain function for sync views and a coroutine function for
    async views, matching the handler's own nature.

    Args:
        condition: Callable receiving request (plus any
            condition_args/condition_kwargs) and returning a bool.
            This can be either a synchronous or asynchronous condition.

        view: The view function or View.run method being decorated.
            Left as None when the decorator is called with arguments,
            e.g. `@condition_required(is_staff, redirect_url="/login")`.

        redirect_url: A fixed route name or path to redirect to when
            the condition fails. Passed through resolve() first,
            falling back to the raw value if resolution fails (e.g.
            it's already a raw path).

        redirect_url_resolver: A callable receiving the request and
            returning the redirect URL as a string. Use this when the
            destination depends on request state, e.g. a next param.

        condition_args: Positional args forwarded to condition after
            request.

        condition_kwargs: Keyword args forwarded to condition after
            request.

    Returns:
        The decorated view, or a decorator awaiting the view if
        called with keyword arguments only.

    Raises:
        ValueError: If both redirect_url and redirect_url_resolver
            are given, or if neither is given and no default is set.
    """
    if redirect_url and redirect_url_resolver:
        raise ValueError("Decorator `condition_required` accepts only one of redirect_url or redirect_url_resolver")

    # Fall back to module-level defaults when neither was provided
    if not redirect_url and not redirect_url_resolver:
        redirect_url = DEFAULT_LOGIN_URL
        redirect_url_resolver = DEFAULT_LOGIN_URL_RESOLVER

    if not redirect_url and not redirect_url_resolver:
        raise ValueError(
            "Decorator `condition_required` requires redirect_url or redirect_url_resolver, "
            "or a default set via set_default_login_url/set_default_login_url_resolver"
        )

    if not callable(condition):
        raise ValueError("Decorator `condition_required` requires a `condition` callable as its first argument e.g. @condition_required(condition)")
    
    condition_args = condition_args or ()
    condition_kwargs = condition_kwargs or {}

    def resolve_redirect_url(request) -> str:
        """
        Determines the redirect target for a failing condition.
        """
        if redirect_url_resolver:
            return redirect_url_resolver(request)
        try:
            return resolve(redirect_url)
        except Exception:
            return redirect_url

    def decorator(fn: Callable) -> Callable:
        """
        Wraps fn with a condition check, matching its calling
        convention (View.run method vs plain function) and sync/async
        nature.
        """
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(first_arg, *args, **kwargs):
                """
                Awaits condition before delegating to fn.
                """
                # Detect calling convention: View.run method vs plain function
                if isinstance(first_arg, View):
                    view_obj = first_arg
                    request = args[0]
                else:
                    view_obj = None
                    request = first_arg

                if not await ensure_async(condition)(request, *condition_args, **condition_kwargs):
                    return redirect(resolve_redirect_url(request))

                if view_obj is not None:
                    return await fn(view_obj, request, **kwargs)
                return await fn(request, *args, **kwargs)
            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(first_arg, *args, **kwargs):
            """
            Calls condition before delegating to fn.
            """
            # Detect calling convention: View.run method vs plain function
            if isinstance(first_arg, View):
                view_obj = first_arg
                request = args[0]
            else:
                view_obj = None
                request = first_arg

            if not ensure_sync(condition)(request, *condition_args, **condition_kwargs):
                return redirect(resolve_redirect_url(request))

            if view_obj is not None:
                return fn(view_obj, request, **kwargs)
            return fn(request, *args, **kwargs)
        return sync_wrapper

    # Support both @condition_required(cond) and @condition_required(cond, redirect_url=...)
    if view is not None:
        return decorator(view)
    return decorator
