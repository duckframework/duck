# Duck Framework

**Duck Framework** is an open-source Python web framework and web server with a built-in reactive UI engine and real-time WebSocket support.

Build high-performance, scalable, server-side reactive web applications — without a separate frontend framework or a complex JavaScript stack.

<details>
<summary><strong>Badges</strong> (click to expand)</summary>

[![Python >=3.10](https://img.shields.io/badge/python->=3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![GitHub stars](https://img.shields.io/github/stars/duckframework/duck?style=social)](https://github.com/duckframework/duck/stargazers)
[![License](https://img.shields.io/github/license/duckframework/duck)](https://github.com/duckframework/duck/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/duckframework/duck/docs.yml?branch=main)](https://github.com/duckframework/duck/actions)
[![Open Issues](https://img.shields.io/github/issues/duckframework/duck)](https://github.com/duckframework/duck/issues)
[![Contributors](https://img.shields.io/github/contributors/duckframework/duck)](https://github.com/duckframework/duck/graphs/contributors)
[![HTTPS](https://img.shields.io/badge/HTTPS-supported-brightgreen.svg)](#)
[![HTTP/2](https://img.shields.io/badge/HTTP--2-supported-brightgreen.svg)](#)
[![WebSocket](https://img.shields.io/badge/WebSocket-supported-brightgreen.svg)](#)
[![Async Views](https://img.shields.io/badge/Async-WSGI%2FASGI-blue.svg)](#)
[![Task Automation](https://img.shields.io/badge/Task-Automation-blueviolet.svg)](#)
[![Content Compression](https://img.shields.io/badge/Compression-gzip%2C%20brotli%2C%20deflate-blue.svg)](#)
[![SSL Auto-Renewal](https://img.shields.io/badge/SSL-Auto%20Renewal-brightgreen.svg)](#)
[![Resumable Downloads](https://img.shields.io/badge/Downloads-Resumable-orange.svg)](#)
[![Security](https://img.shields.io/badge/Security-DoS%2C%20SQLi%2C%20CmdInj-red.svg)](#)
[![Auto Reload](https://img.shields.io/badge/AutoReload-DuckSight-yellow.svg)](#)
[![Django Integration](https://img.shields.io/badge/Django-Integration-blue.svg)](#)
[![Monitoring](https://img.shields.io/badge/Monitoring-CPU%2FRAM%2FDisk%2FI%2FO-brightgreen.svg)](#)

</details>

---

## Quickstart

```sh
pip install duckframework
duck makeproject myproject
cd myproject
python web/main.py # Or simply "duck runserver"
```

Visit **http://localhost:8000** — you're running Duck. For the full walkthrough (install options, project types, what gets generated), see [Getting Started](./readme/getting-started.md).

---

## Documentation

| Guide | What's inside |
|---|---|
| [Getting Started](./readme/getting-started.md) | Install, `makeproject` options (`mini`/`normal`/`full`), starting the server |
| [Understanding the Project](./readme/understanding-the-project.md) | `main.py`, `urls.py`, views, pages, components, templates, static files |
| [Django Integration](./readme/django-integration.md) | Add Duck's HTTP/2, HTTPS, and security features to an existing Django project |
| [Features](./readme/features.md) | Full feature breakdown by category |
| [Roadmap](./readme/roadmap.md) | Upcoming features |
| [AI Guidelines](./readme/ai-guidelines.md) | Using Duck with AI assistants / vibe coding |
| [About & Links](./readme/about.md) | Real-world apps, fun facts, useful links |
| [Contributing](./readme/contributing.md) | Sponsorship, reporting issues, premium components |

---

> **Duck is updated regularly** — check the repo for improvements and bug fixes.
