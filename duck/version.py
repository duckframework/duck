"""
Version module for the Duck package.
"""
import sys

version_num = (2, 1, 1)
version = "%d.%d.%d" % version_num
version_name = "Duck"

pyversion = sys.version.split(" ")[0]
server_version = "{}/{} {}/{}".format(version_name, version, "Python", pyversion)

__version__ = version
