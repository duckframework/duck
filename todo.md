# TODO
- Need to document mailing plus email collection in Duck (duck.utils.email module)
- Need to document cookie consent utility module (duck.utils.cookie_consent)
- Need to document content security policy implementation (duck.csp module)
- Need to make middlewares `async-compatible` without converting sync code to async with `sync_to_async`.
- Need to integrate async-compatible Database ORM like sqlalchemy instead of using Django sync-first ORM.
- Need to add monetization options for Duck framework users.
- Need to improve FCP (First Contentful Paint) for `Lively` Pages. First we show a loading banner on page visit without
  loading the fullpage and then load the fullpage using Lively partial navigation.
- Need to make `FileResponses` trully cacheable, as well as `FileIOStream` from `duck.utils.fileio.FileIOStream`.
- Need to cythonize some of the project parts for improved speed esp., components.
- Need to make **Duck** fully async, especially in component & templates (currently at 89% async compatible, need to enable strictness for component rendering in async mode).
- Make UID assignment exclude head elements and only assign to body elements only (reduce UID assignment redundancy).
