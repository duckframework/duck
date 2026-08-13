# Duck Framework Features

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

## 🔮 Upcoming Features

1. **HTTP/3 with QUIC** — faster, modern transport for improved performance
2. **QUIC WebTransport** — a next-gen alternative to WebSockets for real-time communication
3. **Component pre-rendering system** — preload components on a background thread to reduce initial load times of component trees
4. **MQTT (Message Queuing Telemetry Transport) integration** — run your own broker and manage IoT devices with ease
5. **Duck WebApp ➝ APK** — easily convert a Duck web application to an APK
6. **DuckSight hot reload** — hot reload for the DuckSight Reloader instead of a full reload on file changes, for faster, more efficient dev cycles
7. **Internal updates** — securely list and apply updates using cryptographic code signing (e.g. TUF) to verify GitHub-sourced updates, protecting against rollbacks and man-in-the-middle attacks
8. **Complete reverse proxy server** — Duck currently proxies only Django; the goal is a full-fledged reverse proxy server with optional sticky sessions
9. Implement Duck AI Agent system with reusable agents, MCP tool integration, task execution, and long-running worker support.
10. Need to add analytics like web visits, etc to DASHBOARD.
11. **...and more** — [request a feature](../feature_request.md)
