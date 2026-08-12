# Getting Started

## Installation

**Install the latest version from GitHub:**

```sh
pip install git+https://github.com/duckframework/duck.git
```

**Or install from PyPI:**

```sh
pip install duckframework
```

---

## Project Creation

```sh
duck makeproject myproject
```

This creates a `normal` project named `myproject`. You can also create other project types:

- `--full` — a full-featured project
- `--mini` — a simplified starter project

### Full Project

Includes everything Duck offers. Recommended for experienced developers.

```sh
duck makeproject myproject --full
```

### Mini Project

Beginner-friendly, with essential functionality only.

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

This starts the server at **http://localhost:8000**.

Duck serves a basic site by default — explore more in the [documentation](https://docs.duckframework.com/main).

---

**Next:** [Understanding the Project](./understanding-the-project.md) — walks through the files `makeproject` generated.
