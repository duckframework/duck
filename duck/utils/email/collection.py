"""
# Email collection utility.

Provides an interface for registering callbacks that handle email collection,
supporting both synchronous and asynchronous usages.

## Example:

```py
# urls.py / some entry module
from duck.utils.email.collection import EmailCollector

def collect(email, category = None):
    # Do your logic for saving email e.g. saving to a Database
    pass
    
async def async_collect(email, category = None):
    # Do your async logic for saving email e.g. saving to a Database
    pass

# Register callbacks for saving emails.
EmailCollector.register(collect) # Register sync callback
EmailCollector.register(async_collect) # Register async callback
```

```py
# some module
from duck.utils.email.collection import async_collect_email, collect_email

# From some callback, collect email
def process_request(request):
    # Do some request processing
    email = request.POST.get("email")
    collect_email(email, category="Newsletter")


async def async_process_request(request):
    # Do some request processing
    email = request.POST.get("email")
    await async_collect_email(email, category="Newsletter")
 
```

## Obligations When Collecting Emails

When collecting email addresses from users, you have important legal and ethical obligations, including:

- **Transparency:** Clearly inform users why their email is being collected and how it will be used.
- **Consent:** Obtain explicit consent from users before collecting or using their emails, especially for marketing or newsletters.
- **Data Minimization:** Only collect email addresses (and related data) that are strictly necessary for your stated purpose.
- **Security:** Store collected emails securely and protect them from unauthorized access or breaches.
- **Privacy Compliance:** Follow relevant data protection laws (such as GDPR, CCPA, etc.), including providing users with access to, and the ability to delete, their data upon request.
- **No Unsolicited Communication:** Do not send unsolicited emails or share user emails with third parties without explicit permission.

Respecting user privacy builds trust and helps you stay compliant with global regulations.

"""
from typing import Callable, Optional, Awaitable, Union, List, Tuple
from duck.contrib.sync import iscoroutinefunction


def collect_email(email: str, category: Optional[str] = None):
    """
    Shortcut to collect an email synchronously.
    """
    EmailCollector.collect_email(email, category)


async def async_collect_email(email: str, category: Optional[str] = None):
    """
    Shortcut to collect an email asynchronously.
    """
    await EmailCollector.async_collect_email(email, category)


class EmailCollector:
    """
    Email collection utility.

    Provides an interface for registering callbacks that handle email collection,
    supporting both synchronous and asynchronous usages, plus email storage and retrieval.
    """
    _sync_callback: Optional[Callable[[str, Optional[str]], None]] = None
    _async_callback: Optional[Callable[[str, Optional[str]], Awaitable[None]]] = None
    _emails: List[Tuple[str, Optional[str]]] = []

    @classmethod
    def register(cls, callback: Union[Callable[[str, Optional[str]], None], Callable[[str, Optional[str]], Awaitable[None]]]):
        """
        Register a callback for email collection.

        Args:
            callback (Callable): A synchronous or asynchronous callable to call on email collection.

        Raises:
            AssertionError: If callback is not callable.
        """
        assert callable(callback), "Argument `callback` must be a callable."
        if iscoroutinefunction(callback):
            cls._async_callback = callback
        else:
            cls._sync_callback = callback

    @classmethod
    def collect_email(cls, email: str, category: Optional[str] = None):
        """
        Collect an email using the registered synchronous callback.

        Args:
            email (str): The email address to collect.
            category (Optional[str]): The category of the email collection.

        Raises:
            TypeError: If a synchronous callback is not registered.
        """
        if cls._sync_callback is None:
            raise TypeError("Synchronous email collection callback not set. Please use `register` to register a new synchronous callback.")
        if iscoroutinefunction(cls._sync_callback):
            raise RuntimeError("Email collection callback must be synchronous. Use `async_collect_email` for async callbacks.")
        cls._emails.append((email, category))
        cls._sync_callback(email, category)

    @classmethod
    async def async_collect_email(cls, email: str, category: Optional[str] = None):
        """
        Collect an email using the registered asynchronous callback.

        Args:
            email (str): The email address to collect.
            category (Optional[str]): The category of the email collection.

        Raises:
            TypeError: If an asynchronous callback is not registered.
        """
        if cls._async_callback is None:
            raise TypeError("Asynchronous email collection callback not set. Please use `register` to register a new async callback.")
        if not iscoroutinefunction(cls._async_callback):
            raise RuntimeError("Email collection callback must be asynchronous. Use `collect_email` for sync callbacks.")
        cls._emails.append((email, category))
        await cls._async_callback(email, category)

    @classmethod
    def get_collected_emails(cls) -> List[Tuple[str, Optional[str]]]:
        """
        Get a list of all collected emails with their categories.
        
        Returns:
            List[Tuple[str, Optional[str]]]: A list of tuples (email, category).
        
        Notes:
            This only returns collected emails within current session. This doesn't persist between
                application life cycle. To get persistent emails, implement custom logic for retrieving emails e.g. retrieving from Database. 
        """
        return list(cls._emails)
