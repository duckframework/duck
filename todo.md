# TODO
- Need to document mailing plus email collection in Duck (duck.utils.email module)
- Need to document cookie consent utility module (duck.utils.cookie_consent)
- Need to document content security policy implementation (duck.csp module)
- Need to make middlewares `async-compatible` without converting sync code to async with `sync_to_async`.
- Need to integrate async-compatible Database ORM like sqlalchemy instead of using Django sync-first ORM.
- Need to add monetization options for Duck framework users.
- Need to improve FCP (First Contentful Paint) for `Lively` Pages. First we show a loading banner on page visit without
  loading the fullpage and then load the fullpage using Lively partial navigation.
