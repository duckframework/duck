# Duck Framework

**Duck Framework** is an open-source Python web framework and web server with a built-in reactive UI engine and real-time WebSocket support.

Build high-performance, scalable, server-side reactive web applications — without a separate frontend framework or a complex JavaScript stack.

[![Python >=3.10](https://img.shields.io/badge/python->=3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![GitHub stars](https://img.shields.io/github/stars/duckframework/duck?style=social)](https://github.com/duckframework/duck/stargazers)
[![License](https://img.shields.io/github/license/duckframework/duck)](https://github.com/duckframework/duck/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/duckframework/duck/docs.yml?branch=main)](https://github.com/duckframework/duck/actions)

*(More badges — security, performance, integrations — on the [Features](./readme/features.md) page.)*

---

## Quickstart

```sh
# Install Duck Framework
pip install duckframework

# Create a project
duck makeproject myproject

# Change directory to myproject
cd myproject

# Run the webserver
python web/main.py # Optionally use duck runserver
```

Visit **http://localhost:8000** — you're running Duck. For the full walkthrough (install options, project types, what gets generated), see [Getting Started](./docs/getting-started.md).

---

## Documentation

New to Duck? Start with **Getting Started**, then **Understanding the Project** — that's really all you need to build your first app. The rest is there when you need it.

- 🟢 **[Getting Started](./readme/getting-started.md)** — install Duck, create a project, and start the server
- 🟢 **[Understanding the Project](./readme/understanding-the-project.md)** — what each generated file does: `main.py`, `urls.py`, views, pages, components, templates, static files
- 🔵 [Django Integration](./readme/django-integration.md) — add Duck's HTTP/2, HTTPS, and security features to an existing Django project
- 🔵 [Features](./readme/features.md) — full feature breakdown, plus what's coming next
- 🔵 [AI Guidelines](./readme/ai-guidelines.md) — using Duck with AI assistants / vibe coding
- ⚪ [About & Links](./readme/about.md) — real-world apps, fun facts, useful links
- ⚪ [Contributing](./readme/contributing.md) — sponsorship, reporting issues, premium components
- ⚪ [Official Documentation](https://docs.duckframework.com) — full documentation

🟢 = start here &nbsp;·&nbsp; 🔵 = once you're building &nbsp;·&nbsp; ⚪ = optional reading

---

> **Duck is updated regularly** — check the repo for improvements and bug fixes.
