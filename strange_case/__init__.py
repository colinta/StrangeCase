from strange_case.registry import Registry
from strange_case.extensions import *
from strange_case.support import *
from strange_case.nodes import *
from strange_case.processors import *
from strange_case.__main__ import run


def output_error(msg):
    import sys
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)
    sys.exit(1)


def require_package(pkg):
    output_error("\033[1m" + pkg + "\033[0m is required.\n  > pip install " + pkg)
