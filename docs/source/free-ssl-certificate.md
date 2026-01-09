# 🔐 Free SSL Certificate

**Duck** provides seamless support for **Let's Encrypt SSL certificates** with automatic and lifetime renewals using `certbot` in combination with **Duck automation** and **blueprints**.

## Obtaining SSL Certificate

To get started, install `certbot` via `pip`:

```bash
pip install certbot
```

`certbot` allows you to request SSL certificates from [Let's Encrypt](https://letsencrypt.com) and handles domain verification to ensure you own the domain.

To pass domain verification, Duck uses the `webroot` plugin. This plugin works by placing random verification files in a directory that is publicly accessible—similar to serving static files.

``` {important}
Before continuing, make sure you’ve defined `SSL_CERTFILE_LOCATION` and `SSL_PRIVATE_KEY_LOCATION` in your `settings.py`.
```

``` {important}
If Certbot is not available yet you installed it, you can point directly to Certbot executable by setting `CERTBOT_EXECUTABLE` in settings configuration.
```

---

## Domain Verification Setup

**Duck** simplifies verification with built-in support. Just enable the **Certbot blueprint** in your settings:

```py
# settings.py

BLUEPRINTS = [
    "duck.etc.apps.certbot.blueprint.Certbot",
    # other blueprints...
]
```

``` {important}
Don’t forget to set `CERTBOT_ROOT` in your settings. This directory will be used by Certbot to place verification files.
```

---

## Generating SSL Certificate

Once setup is complete, you can automate certificate generation and renewal using Duck’s built-in automation system. In your `settings.py`, add:

```py
# settings.py

ENABLE_AUTOMATIONS = True

CERTBOT_ROOT = BASE_DIR / "etc/certbot"

CERTBOT_EMAIL = "your_email@domain.com"

AUTOMATIONS = {
    "duck.etc.automations.ssl.CertbotAutoSSL": {
        "trigger": "duck.automation.trigger.NoTrigger",
    },
    # other automations...
}
```

This automation checks if a certificate is missing or expired. If so, it requests a new one and continues to renew it periodically before expiration.

``` {note}
Do not forget to set `CERTBOT_ROOT` and `CERTBOT_EMAIL` in your settings configuration. Also remember to set your 
domain when using the `duck runserver` command. This can be done by providing the `-d` argument to `runserver` command.
```

``` {important}
The above configuration is the default for HTTP only. For HTTPS, make sure `ENABLE_HTTPS` and `FORCE_HTTPS` is set to `True` in settings configuration.
Also, ensure that `FORCE_HTTPS_BIND_PORT` is set port `80` and your web application is set to run stricty on port `443`, meaning, the `HTTPS redirection` will be pointing from port `80 -> 443`.
```

**HTTPS Example:**

```py
ENABLE_HTTPS = True

FORCE_HTTPS = True

FORCE_HTTPS_BIND_PORT = 80
```

> After renewal, your new SSL configuration will be used on all new connections.

---

## Final Configuration Overview

Your final `settings.py` should look like this:

```py

BASE_DIR = BaseDir()

SSL_CERTFILE_LOCATION = BASE_DIR / "etc/ssl/server.crt"

SSL_PRIVATE_KEY_LOCATION = BASE_DIR / "etc/ssl/server.key"

CERTBOT_ROOT = BASE_DIR / "etc/certbot"

CERTBOT_EMAIL = "your_email@domain.com"

ENABLE_AUTOMATIONS = True

BLUEPRINTS = [
    "duck.etc.apps.certbot.blueprint.Certbot",
    # other blueprints...
]

AUTOMATIONS = {
    "duck.etc.automations.ssl.CertbotAutoSSL": {
        "trigger": "duck.automation.trigger.NoTrigger",
    }, # Generates/renews certificates
    # other automations...
}
```

---

## Debugging

For debugging purposes, you can parse extra arguments to `certbot` command by setting `CERTBOT_EXTRA_ARGS` in settings configuration. This is a list of arguments (strings) to add to `certbot` command, e.g. `-v` argument for verbose logs.


---

## Tips & Notes

- **Certificates renew automatically** every 30 days; no manual action is needed.
- **No restarts required**: Duck hot-reloads certificates, keeping uptime high.
- **Easy integration**: Blueprints and automations are plug-and-play.
