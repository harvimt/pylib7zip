"""Wrapper on 7-Zip IInArchive."""
from __future__ import unicode_literals, absolute_import, \
    division, print_function
from future.builtins import *  # noqa


class Archive(object):

    """Represents a 7-Zip IInArchive."""

    def __init__(self, file):
        """Create an archive referencing file."""
        self.file = file
