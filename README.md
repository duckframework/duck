# Duck Framework
[![Python >=3.10](https://img.shields.io/badge/python->=3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![GitHub stars](https://img.shields.io/github/stars/duckframework/duck?style=social)](https://github.com/duckframework/duck/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/duckframework/duck?style=social)](https://github.com/duckframework/duck/network/members)
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
[![DuckSight Hot Reload](https://img.shields.io/badge/HotReload-DuckSight-yellow.svg)](#)
[![Django Integration](https://img.shields.io/badge/Django-Integration-blue.svg)](#)
[![Monitoring](https://img.shields.io/badge/Monitoring-CPU%2FRAM%2FDisk%2FI%2FO-brightgreen.svg)](#)

**Duck** is a powerful, open-source, full-fledged Python-based **web server**, **framework**, and **reverse proxy** designed for building modern, customizable web applications — from small sites to large-scale platforms.  

**It simplifies web development with:**

1. [**Built-in HTTPS support**](https://docs.duckframework.xyz/main/https-and-http2) for secure connections  
2. **Native HTTP/2 support** with **HTTP/1** backward compatibility [link](https://docs.duckframework.xyz/main/https-and-http2)  
3. Hassle-free **free SSL certificate generation** with **automatic renewal** [link](https://docs.duckframework.xyz/main/free-ssl-certificate)  
4. [**Lively Component System**](https://docs.duckframework.xyz/main/lively-components) — with `VDom Diffing` (support for fast UI's) 
5. [**WebSocket support**](https://docs.duckframework.xyz/main/websocket) — modern websocket implementation with `per-message compression`.
6. Built-in [task automation](https://docs.duckframework.xyz/main/automations) — no need for [cron jobs](https://en.m.wikipedia.org/wiki/Cron)  
7. Automatic **content compression** using `gzip`, `deflate` or `brotli`
8. Support for **chunked transfer encoding**  
9. Easy integration with existing **Django** projects using [`django-add`](https://docs.duckframework.xyz/main/django-integration) command.
10. Organized routing with **Duck** [`Blueprints`](https://docs.duckframework.xyz/main/blueprint)
11. Full support for **async views** or asynchronous code even in [`WSGI`](https://docs.duckframework.xyz/main/wsgi) environment
12. Dynamic project generation with `makeproject` (`mini`, `normal`, or `full`)  
13. Runs on both [`WSGI`](https://docs.duckframework.xyz/main/wsgi) and [`ASGI`](https://docs.duckframework.xyz/main/asgi) environments, can even run `async` protocols like `HTTP/2` or `WebSockets` on `WSGI`.  
14. High-performance with low-latency response times  
15. **Resumable downloads** for large files  
16. Protection against **DoS**, **SQL Injection**, **Command Injection**, and other threats  
17. **Auto-reload** in debug mode for rapid development  
18. [**Free production SSL**](https://docs.duckframework.xyz/main/free-ssl-certificate) — no certificate costs  
19. **Automatic SSL renewal** using `certbot` plus Duck automation system
20. Comes with built-in web development tools and helpers  
21. [Log management](https://docs.duckframework.xyz/main/logging) with `duck logs` and file-based logging by default  
22. Real-time [system monitoring](https://docs.duckframework.xyz/main/monitoring) for CPU, RAM, Disk usage, and I/O activity with `duck monitor`
23. Easily generate app sitemap using command [`duck sitemap`](https://docs.duckframework.xyz/main/sitemap) or just use 
       the builtin blueprint [`duck.etc.apps.essentials.blueprint.Sitemap`](https://docs.duckframework.xyz/main/sitemap) for dynamic cached sitemap serving.
24. Comes with independant [micro applications]https://docs.duckframework.xyz/main/microapps) which runs on their own servers for micro services support.
25. Highly **customizable** to fit any use case  

And more — see [feature list](https://duckframework.xyz/features)

## Upcoming Features

1. **HTTP/3 with QUIC** – Faster, modern transport for improved performance.  
2. **QUIC WebTransport** – A next-gen alternative to WebSockets for real-time communication.  
3. **Component Pre-rendering System** – A system to preload components in the background thread to reduce initial load times of component trees.
4. **Customizable Dashboards** – Tailor interfaces to your workflow and preferences.  
5. **MQTT (Message Queuing Telementry Transport) Integration** – Run your own broker and manage IoT devices with ease.  
6. **Duck WebApp to APK** – Easily convert a Duck web application to APK.
7. **DuckSight Hot Reload** – Instead of full reload on file changes, implement **hot reload** for the **DuckSight Reloader**. This is faster and efficient than full reload.
8. **Internal Updates** – Implement logic for listing and securely applying updates when available, utilizing cryptographic code signing (using standards like TUF) to verify GitHub-sourced updates, protecting against rollbacks, and man-in-the-middle exploits.
9. ~~**Worker Processes** – Use of worker processes to utilize all available CPU cores for improved request handling.~~
10. **Complete Reverse Proxy Server** – **Duck** only acts as reverse proxy for  Django only. Need to make Duck a full-fledged reverse proxy server with optional sticky sessions.
11. ~~**Component Mutation Observer** – Need to build an optional component mutation observer for keeping track of child changes for fastest re-render (approx. 75x fast on unchanged children).~~
12. **MCP (Model Context Protocol) Server** – Need to make it easy for creating MCP servers for easy AI communication. 
13. **...and more** – [Request a feature](./feature_request.md)

---

## 🦆 Fun Facts

- The **Duck** official website is powered by the **Duck** framework itself—showcasing a true "dogfooding" approach!
- [**Duck's Lively components**](https://docs.duckframework.xyz/main/lively-components) bring you a **Lively UI** that's exceptionally fast and responsive, eliminating slow page re-rendering for a seamless user experience.

---

## Getting Started

**Install latest version from Github using:**

```sh
pip install git+https://github.com/duckframework/duck.git
```

**Or install from `PyPi` using:**

```sh
pip install duckframework
```

---

## Project Creation

```sh
duck makeproject myproject
```

This creates a `normal` project named `myproject`. You can also create other project types using:

- `--full` for a full-featured project  
- `--mini` for a simplified starter project

### Full Project

The full version includes everything **Duck** offers. Recommended for experienced developers.

```sh
duck makeproject myproject --full
```

### Mini Project

Beginner-friendly. Lightweight version with essential functionality.

```sh
duck makeproject myproject --mini
```

---

## Simple Startup

```sh
duck makeproject myproject
cd myproject
duck runserver   # or: python3 web/main.py
```

This starts the server at **http://localhost:8000**   

**Duck** serves a basic site by default — explore more at [Documentation](https://docs.duckframework.xyz/main)

---

## Django Integration

If you have an existing **Django** project and want production features like **HTTPS**, **HTTP/2**, and **resumable downloads**, Duck makes it easy.  

Unlike `nginx` setups, **Duck** simplifies this with a few commands.

### Benefits

- Native [HTTP/2 & HTTPS](https://docs.duckframework.xyz/main/https-and-http2) implementation. 
- Extra built-in security [middleware](https://docs.duckframework.xyz/main/middlewares) (DoS, SQLi, etc.)  
- Duck and Django run in the same Python environment (faster communication)  
- Auto-compressed responses  
- Resumable large downloads  
- Fast and [Reactive Lively components](https://docs.duckframework.xyz/main/lively-components) - for beautiful & responsive UI.
- [Free SSL with renewal](https://docs.duckframework.xyz/main/free-ssl-certificate)
- and more

### Usage

```sh
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

### Notes:

- Follow instructions provided by `django-add` command carefully  
- Make sure your Django project defines at least one `urlpattern`
- Once setup, you’re good to go!

---

## Duck Official Site

Visit: [https://duckframework.xyz](https://duckframework.xyz)    
Docs: [https://docs.duckframework.xyz](https://docs.duckframework.xyz)
Lively UI Docs: https://docs.duckframework.xyz/main/lively-components   

---

## 🚀 Premium Duck Components Coming Soon!
>  
> All our UI components are currently free and open source. Stay tuned for upcoming Pro Packs featuring advanced dashboards, e-commerce, and integrations!
>
> ⭐ Star this repo to get notified on release!


## Contributing & Issues

**Duck** is open to all forms of contribution — financial or technical.

### Sponsorship/Donations:  

Support development at [Open Collective](https://opencollective.com/duckframework/contribute)  

### Report issues:  

Use the [GitHub Issues page](https://github.com/duckframework/duck/issues)

---

> **Duck is updated regularly** — check the repo for improvements and bug fixes.
