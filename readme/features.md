# Duck Framework Features

## 🚀 Build Faster, Ship Sooner

1. Dynamic project generation with `makeproject` (`mini`, `normal`, or `full`)
2. Easy integration with existing **Django** projects via the [`django-add`](https://docs.duckframework.com/main/django-integration) command
3. Organized routing with Duck [`Blueprints`](https://docs.duckframework.com/main/blueprint)
4. Built-in web development tools and helpers
5. [**MCP (Model Context Protocol) server**](https://docs.duckframework.com/main/mcp) — make it easy to build MCP servers for seamless AI communication
6. [**Builtin Dashboard**](https://docs.duckframework.com/main/dashboard) — tailor interfaces to your workflow and preferences
7. [Official MCP Server](https://duckframework.com/blog/official-duck-framework-mcp-server-now-available) at https://duckframework.com/mcp

## ⚡ Reactive & High Performance

1. [**Lively Component System**](https://docs.duckframework.com/main/lively-components) with `VDom diffing` for fast UI updates
2. [**WebSocket support**](https://docs.duckframework.com/main/websocket) — a modern implementation with per-message compression
3. **Component mutation observer** — an optional mutation observer to track child changes for faster re-renders (75x faster on unchanged children)
4. Automatic **content compression** using `gzip`, `deflate`, or `brotli`
5. Support for **chunked transfer encoding**
6. High performance with low-latency response times
7. **Resumable downloads** for large files
8. **Worker processes/threads** — use worker processes/threads to utilize all available CPU cores for improved request handling

## 🌐 Modern Web Platform

1. [**Built-in HTTPS support**](https://docs.duckframework.com/main/https-and-http2) for secure connections
2. **Native HTTP/2 support** with **HTTP/1** backward compatibility — [details](https://docs.duckframework.com/main/https-and-http2)
3. Hassle-free **free SSL certificate generation** with **automatic renewal** — [details](https://docs.duckframework.com/main/free-ssl-certificate)
4. [**Free production SSL**](https://docs.duckframework.com/main/free-ssl-certificate) — no certificate costs
5. **Automatic SSL renewal** using `certbot` plus Duck's automation system
6. Runs on both [`WSGI`](https://docs.duckframework.com/main/wsgi) and [`ASGI`](https://docs.duckframework.com/main/asgi) — can even serve async protocols like `HTTP/2` or WebSockets over WSGI
7. Full support for **async views** and asynchronous code, even in a [`WSGI`](https://docs.duckframework.com/main/wsgi) environment

## 🔒 Secure by Default

1. Protection against **DoS**, **SQL injection**, **command injection**, and other threats
2. **JWT (JSON Web Token) authentication** — persistent logins via [JWT](https://docs.duckframework.com/main/jwt).

## ⚙️ Automation & Operations

1. Built-in [task automation](https://docs.duckframework.com/main/automations) — no need for [cron jobs](https://en.m.wikipedia.org/wiki/Cron)
2. [Log management](https://docs.duckframework.com/main/logging) via `duck logs`, with file-based logging by default
3. Real-time [system monitoring](https://docs.duckframework.com/main/monitoring) for CPU, RAM, disk usage, and I/O activity via `duck monitor`
4. Built-in [dashboard](https://docs.duckframework.com/main/dashboard) for monitoring requests, latency, and system metrics
5. **Dependency synchronization** with [`duck sync`](https://docs.duckframework.com/main/cli/sync) — manage project dependencies from a `duck.toml` manifest, automatically detecting the environment and installing missing Python and system packages
6. Instant sitemap generation via [`duck sitemap`](https://docs.duckframework.com/main/sitemap), or the built-in [`duck.etc.blueprints.essentials.blueprint.Sitemap`](https://docs.duckframework.com/main/sitemap) blueprint for dynamic, cached sitemap serving
7. **Auto-reload** in debug mode for rapid development

## 🏗️ Scalable Architecture

1. Independent [microapps](https://docs.duckframework.com/main/microapp) that run on their own servers, for microservices support
2. Highly **customizable** to fit any use case
