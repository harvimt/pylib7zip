"""Utilities to reduce redundancy."""
from __future__ import unicode_literals, absolute_import, \
    division, print_function
from future.builtins import *  # noqa
from ._lib7zip import _lib7zip


def RNOK(hresult):
    """Raise an error if not S_OK."""
    if hresult != _lib7zip.S_OK:
        raise RuntimeError("HRESULT error, hresult=%x", hresult)
