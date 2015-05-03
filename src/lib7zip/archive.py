"""Wrapper on 7-Zip IInArchive."""
from __future__ import unicode_literals, absolute_import, \
    division, print_function
from future.builtins import *  # noqa
import weakref

from ._lib7zip import _lib7zip, ffi
from ._utils import RNOK

class Archive(object):

    """Represents a 7-Zip IInArchive."""

    def __init__(self, file):
        """Create an archive referencing file."""
        self._file = None
        try:
            file.fileno()
        except AttributeError:
            file = open(str(file), 'rb')
        self.stream = _lib7zip.create_instream_from_file(file)
        assert self.stream != ffi.NULL

    def __enter__(self):
        """Act as a contextmanager."""
        pvar = ffi.gc(_lib7zip.create_propvariant(), _lib7zip.destroy_propvariant)
        num_items = ffi.new("uint32_t*")

        # FIXME
        RNOK(_lib7zip.GetNumberOfFormats(num_items))
        for i in range(num_items[0]):
            RNOK(_lib7zip.GetHandlerProperty2(i, _lib7zip.NArchive_kName, pvar))
            if ffi.string(pvar.bstrVal) == "7z":
                break

        RNOK(_lib7zip.GetHandlerProperty2(i, _lib7zip.NArchive_kClassID, pvar))
        self.archive_p = ffi.new("void**")

        RNOK(_lib7zip.CreateObject(
            pvar.puuid,
            ffi.addressof(_lib7zip.IID_IInArchive),
            self.archive_p,
        ))
        self.archive = ffi.cast("IInArchive*", self.archive_p[0])
        return self

    def __exit__(self, *args, **kwargs):
        """Cleanup when acting as context manager."""
        RNOK(_lib7zip.archive_close(self.archive))
        self.archive_p = None
        self.stream = None

    def __len__(self):
        """Return number of items in the archive."""
        num_items = ffi.new("uint32_t*")
        RNOK(_lib7zip.archive_get_num_items(self.archive, num_items))
        return num_items[0]

    def __getitem__(self, index):
        """Get ArchiveItem at index."""
        return ArchiveItem(self, index)

    def extract(self, directory):
        """Extract entire archive to directory."""
        pass

class ArchiveItem(object):
    """Represents an item in an Archive."""
    __slots__ = ('archive', 'index')
    def __init__(self, archive, index):
        self.archive = weakref.ref(archive)
        self.index = index

    def extract(self, extract_to):
        pass
