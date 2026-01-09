# 🚀 Getting Started

## Installation

**Install Duck using uv**:

```bash
git clone https://github.com/duckframework/duck.git
uv pip install ./duck # Or just use pip
```

**Alternatively, use**:

```bash
pip install git+https://github.com/duckframework/duck.git
```

## Requirements

``` {note}
**Duck** requires `Python>=3.10` for it to work seamlessly.
```

Before using **Duck**, ensure the following dependencies are installed. These packages will be automatically installed when you install Duck.


```bash
Django>=5.1.5
Jinja2>=3.1.5
watchdog>=4.0.1
requests>=2.31.0
h2>=4.2.0
asgiref>=3.8.1
psutil>=7.0.0
msgpack>=1.1.1
rich>=14.1.0
diskcache
colorama
tzdata
click
setproctitle
```

---

### Starting Project

To run a Duck web application/server, you need to start by creating a project.

**To quickly start a new project, run:**

```bash
duck makeproject myproject
```

#### Duck makeproject types

1. **Normal project:**

This project type is the Duck's default project that will be created when you create a project without any extra arguments. This version of a project create a normal average project with a sense of not making beginners too overwhelmed with the project confifuration.

```bash
duck makeproject myproject
```

2. **Mini project:**

This project type has lesser files and directories, meaning less configuration, making it easy for beginners to understand the workflow if they turn up to be overwhelmed by the normal Duck project. You may also use this project type for those simple web applictions which doesn't require much of Duck's configurations.

```bash
duck makeproject myproject --mini
```

3. **Full project**:

This is the absolute, complete and full project type which has full configuration of Duck. This is very useful for complex web applications which require more of quickstart configurations for efficiency and optimized solutions. This project type does not limit small to medium or simple web applications. You may use this project type if you want to have more control of your web application as this gives you upto 95% more customization compared to other project types.

```sh
duck makeproject myproject --full
```

---

### Running the application

By default every project comes up with a `main.py` file located at `web/main.py` in the root directory.

**Here is what the main.py looks like:**

```py
#!/usr/bin/env python
"""
Main py script for application creation and execution.
"""

from duck.app import App

app = App(port=8000, addr="0.0.0.0", domain="localhost")

if __name__ == "__main__":
    app.run()

```

You can run the **Duck** application by directly executing the `main.py` or use
the command `duck runserver` from within the app root directory.


#### Notes

- Running command `duck runserver ...` does not execute the `main.py` unless flag `--file` is provided.
- Command `runserver` executes the app from terminal using explicitly provided terminal arguments.

---

### Running tests

**Duck** comes with builtin test cases which you can use to check if **Duck** is working correctly. This can be done as follows: 

```bash
duck runtests
```

The above code tries to run default test cases for the server and it must output that everything went `OK`. To stop the server responsible for 
handling the tests, you need to do `CTRL-C` (this shutdowns the test server).  

You can parse argument `-v` to make `duck runtests -v` for verbose logs. This is useful for finding where the code failed in cases there was a 
failure in the tests. **Duck** `runtests` command can also be used for testing compatibility issues within your platform especially **python version compatibility** issues.

> If you have encountered an error with `duck runtests` command on a compatible python environment (`python3.10+`). Do not hesitate to open an [issue](https://github.com/duckframework/duck/issues) so that
> we will get the issue fixed right away. 

---
