"""
**Duck** is a powerful, open-source, full-fledged Python-based **web server**, **framework**, and **reverse proxy** designed for building modern, customizable web applications — from small sites to large-scale platforms.

With **Duck**, developers can quickly deploy secure, high-performance applications with minimal 
configuration. Ideal for creating scalable, secure, and customizable **web solutions**, **Duck** 
streamlines the development process while ensuring top-notch security and performance.

## Quick Start Example

To start using Duck, initialize an ``App`` instance with your desired port and address, 
then run the application:

```py
from duck.app import App

app = App(port=5000, addr='127.0.0.1', domain='localhost')

if __name__ == '__main__':
    app.run()
```
"""
import sys
import pathlib

from duck.version import version


__author__ = "Brian Musakwa"
__email__ = "digreatbrian@gmail.com"
__version__ = version

# Add current directory or parent directory to pythonpath
# This is critical for resolving modules inside the project.
original_curdir = curdir = pathlib.Path(".").resolve()
original_curdir = str(original_curdir)
curdir_endswith_web = False

if curdir.parts[-1] == "web":
    # Maybe we are inside `web` directory e.g. someapp/web so 
    # lets add the basedir/parent instead
    curdir = curdir.parent
    curdir_endswith_web = True

if curdir not in sys.path:
    sys.path.insert(0, str(curdir))
    
    if curdir_endswith_web and original_curdir not in sys.path:
        # Also add the original directory as second to the stripped curdir
        if original_curdir not in sys.path:
            sys.path.insert(1, original_curdir)
