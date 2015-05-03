import logging
logger = logging.getLogger(__name__)

import os.path
import pytest
from lib7zip._lib7zip import _lib7zip, ffi
from lib7zip._utils import RNOK

BASEDIR = os.path.join(os.path.dirname(__file__), 'files')


def open_test_file(path, mode='rb'):
    return open(os.path.join(BASEDIR, path), "rb")


@ffi.callback('void(const char*)')
def log_debug_cb(msg):
    logger.debug(ffi.string(msg).decode('utf8'))


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    _lib7zip.set_logger_cb(log_debug_cb)


def test_version():
    version = ffi.string(_lib7zip.C_MY_7ZIP_VERSION)
    logger.debug(version)


def test_raw_all():
    global logger
    pvar = ffi.gc(_lib7zip.create_propvariant(), _lib7zip.destroy_propvariant)
    with open_test_file('abc.7z') as f:
        logger.debug("Creating stream...")
        stream = _lib7zip.create_instream_from_file(f)
        assert stream != ffi.NULL
        logger.debug("...Created")
        logger.debug("Creating archive...")
        num_items = ffi.new("uint32_t*")
        RNOK(_lib7zip.GetNumberOfFormats(num_items))
        logger.debug("num_items=%d", num_items[0])
        for i in range(num_items[0]):
            logger.debug("i=%d", i)
            RNOK(_lib7zip.GetHandlerProperty2(i, _lib7zip.NArchive_kName, pvar))
            logger.debug("type=%s", ffi.string(pvar.bstrVal))
            if ffi.string(pvar.bstrVal) == "7z":
                logger.debug("found it")
                break

        logger.debug("Creating Archive Object...")
        RNOK(_lib7zip.GetHandlerProperty2(i, _lib7zip.NArchive_kClassID, pvar))
        archive_p = ffi.new("void**")

        RNOK(_lib7zip.CreateObject(
            pvar.puuid,
            ffi.addressof(_lib7zip.IID_IInArchive),
            archive_p,
        ))
        archive = ffi.cast("IInArchive*", archive_p[0])
        assert archive != ffi.NULL
        logger.debug("...Created")
        logger.debug("Opening...")
        _lib7zip.archive_open(
            archive, stream, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL)
        logger.debug("...Opened")
        RNOK(_lib7zip.archive_get_num_items(archive, num_items))
        logger.debug("num_items=%d", num_items[0])
        for i in range(num_items[0]):
            logger.debug("i=%d", i)
            RNOK(_lib7zip.archive_get_item_property_pvar(
                archive, i, _lib7zip.kpidPath, pvar))
            assert pvar.vt == _lib7zip.VT_BSTR
            logger.debug("path=%s", ffi.string(pvar.bstrVal))
        logger.debug("Closing...")
        RNOK(_lib7zip.archive_close(archive))
        logger.debug("...Closing")
