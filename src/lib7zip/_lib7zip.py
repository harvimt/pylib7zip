"""
This contains all the CFFI build code, like setting up the verifier.
"""
from __future__ import unicode_literals, absolute_import, \
    division, print_function
from future.builtins import *  # noqa
import binascii
import sys
import threading
import os.path

from cffi import FFI
from cffi.verifier import Verifier
ffi = FFI()
ffi.set_unicode(True)

SRCDIR = os.path.dirname(os.path.dirname(__file__))
P7ZIPSOURCE = 'p7zip_9.20.1'


def _create_modulename(cdef_sources, source, sys_version):
    """
    This is the same as CFFI's create modulename except we don't include the
    CFFI version.
    """
    from .__about__ import __title__
    key = '\x00'.join([sys_version[:3], source, cdef_sources])
    key = key.encode('utf-8')
    k1 = hex(binascii.crc32(key[0::2]) & 0xffffffff)
    k1 = k1.lstrip('0x').rstrip('L')
    k2 = hex(binascii.crc32(key[1::2]) & 0xffffffff)
    k2 = k2.lstrip('0').rstrip('L')
    return '_{}_cffi_{}{}'.format(__title__, k1, k2)


def _compile_module(*args, **kwargs):
    raise RuntimeError(
        "Attempted implicit compile of a cffi module. All cffi modules should "
        "be pre-compiled at installation time."
    )


class LazyRawLib7zip(object):
    """
    Lazy reference to the raw 7zip library
    """
    def __init__(self, ffi):
        self._ffi = ffi
        self._lib = None
        self._lock = threading.Lock()

    def __getattr__(self, name):
        if self._lib is None:
            with self._lock:
                if self._lib is None:
                    self._lib = self._ffi.verifier.load_library()

        return getattr(self._lib, name)

CDEFS = []

with open(os.path.join(SRCDIR, "windowsdefs.h")) as f:
    CDEFS.append(f.read())

with open(os.path.join(SRCDIR, P7ZIPSOURCE, "CPP/7zip/PropID.h")) as f:
    CDEFS.append('\n'.join(l for l in f if not l.startswith('#')))

CDEFS.append("""
#define MY_VER_MAJOR ...
#define MY_VER_MINOR ...
#define MY_VER_BUILD ...
const char* C_MY_VERSION;
const char* C_MY_7ZIP_VERSION;
const char* C_MY_DATE;
const char* C_MY_COPYRIGHT;
const char* C_MY_VERSION_COPYRIGHT_DATE;

const char* C_P7ZIP_VERSION;

void set_logger_cb(void(const char*));

const GUID IID_IInArchive;

enum {
    NArchive_kName = 0,
    NArchive_kClassID,
    NArchive_kExtension,
    NArchive_kAddExtension,
    NArchive_kUpdate,
    NArchive_kKeepName,
    NArchive_kStartSignature,
    NArchive_kFinishSignature,
    NArchive_kAssociate
};

uint32_t GetNumberOfFormats(uint32_t*);
uint32_t GetNumberOfMethods(uint32_t *);
uint32_t GetMethodProperty(uint32_t index, uint32_t propID, void * value);
uint32_t GetHandlerProperty2(uint32_t, uint32_t propID, void *);
uint32_t CreateObject(GUID *, GUID *, void **);

PROPVARIANT* create_propvariant();
void destroy_propvariant(PROPVARIANT*);

typedef struct IInArchive IInArchive;
typedef struct IInStream IInStream;

//IInStream
typedef HRESULT (*_stream_read_callback)
    (void* self, void *data, uint32_t size, uint32_t *processedSize);
typedef HRESULT (*_stream_seek_callback)
    (void* self, uint64_t offset, int32_t seekOrigin, uint64_t *newPosition);
typedef HRESULT (*_stream_get_size_callback)(void* self, uint64_t *size);

IInStream* create_instream_from_file(FILE* file);

//IArchiveOpenCallback
typedef HRESULT (*_set_total_callback)
    (void* self, const uint64_t * files, const uint64_t * bytes);
typedef HRESULT (*_set_completed_callback)
    (void* self, const uint64_t * files, const uint64_t * bytes);
typedef HRESULT (*_get_password_callback)(void* self, wchar_t** password);

//IInArchive
void archive_release(IInArchive* archive);
HRESULT archive_open(
    IInArchive* archive,
    IInStream* in_stream,
    void* data /* optional - passed to callbacks as first arg */,
    wchar_t* password, /* optional */
    /* optional - takes precedence over password */
    _get_password_callback get_password_callback,
    _set_total_callback set_total_callback, /* optional */
    _set_completed_callback set_completed_callback /* optional */);

HRESULT archive_get_num_items(IInArchive* archive, uint32_t* num_items);
HRESULT archive_get_item_property_pvar(
    IInArchive* archive, uint32_t index, uint32_t prop, PROPVARIANT* pvar);

HRESULT archive_close(IInArchive*);
""")

SOURCE = """
#include "windowsdefs.h"
#include "clib7zip.h"
#include "7zip/MyVersion.h"

const char* C_MY_VERSION = MY_VERSION;
const char* C_MY_7ZIP_VERSION = MY_7ZIP_VERSION;
const char* C_MY_DATE = MY_DATE;
const char* C_MY_COPYRIGHT = MY_COPYRIGHT;
const char* C_MY_VERSION_COPYRIGHT_DATE = MY_VERSION_COPYRIGHT_DATE;

const char* C_P7ZIP_VERSION = P7ZIP_VERSION;
"""

CDEF = '\n'.join(CDEFS)
ffi.cdef(CDEF)

verify_kwargs = dict(
    modulename=_create_modulename(CDEF, SOURCE, sys.version),
    relative_to=SRCDIR,
    ext_package='lib7zip',
    tmpdir='',
    include_dirs=[
        SRCDIR,
        os.path.join(SRCDIR, P7ZIPSOURCE, 'CPP'),
        os.path.join(SRCDIR, P7ZIPSOURCE, 'CPP/7zip/UI/Client7z'),
        os.path.join(SRCDIR, P7ZIPSOURCE, 'CPP/myWindows'),
        os.path.join(SRCDIR, P7ZIPSOURCE, 'CPP/include_windows'),
    ],
    define_macros=[
        ('_FILE_OFFSET_BITS', '64'),
        ('_LARGEFILE_SOURCE', True),
        ('_REENTRENT', True),
    ],
    sources=[
        os.path.join(SRCDIR, 'clib7zip.cpp'),
    ] + [
        os.path.join(SRCDIR, P7ZIPSOURCE, p)
        for p in [
            'CPP/myWindows/wine_date_and_time.cpp',
            'CPP/myWindows/myGetTickCount.cpp',
            'CPP/Common/CRC.cpp',
            'CPP/Common/IntToString.cpp',
            'CPP/Common/MyMap.cpp',
            'CPP/Common/MyString.cpp',
            'CPP/Common/MyWindows.cpp',
            'CPP/Common/MyXml.cpp',
            'CPP/Common/StringConvert.cpp',
            'CPP/Common/StringToInt.cpp',
            'CPP/Common/UTFConvert.cpp',
            'CPP/Common/MyVector.cpp',
            'CPP/Common/Wildcard.cpp',
            'CPP/Windows/PropVariant.cpp',
            'CPP/Windows/PropVariantUtils.cpp',
            'CPP/Windows/Synchronization.cpp',
            'CPP/Windows/System.cpp',
            'CPP/Windows/Time.cpp',
            'CPP/Windows/FileDir.cpp',
            'CPP/Windows/FileFind.cpp',
            'CPP/Windows/FileIO.cpp',
            'CPP/7zip/Common/InBuffer.cpp',
            'CPP/7zip/Common/InOutTempBuffer.cpp',
            'CPP/7zip/Common/CreateCoder.cpp',
            'CPP/7zip/Common/CWrappers.cpp',
            'CPP/7zip/Common/FilterCoder.cpp',
            'CPP/7zip/Common/LimitedStreams.cpp',
            'CPP/7zip/Common/LockedStream.cpp',
            'CPP/7zip/Common/MethodId.cpp',
            'CPP/7zip/Common/MethodProps.cpp',
            'CPP/7zip/Common/MemBlocks.cpp',
            'CPP/7zip/Common/OffsetStream.cpp',
            'CPP/7zip/Common/OutBuffer.cpp',
            'CPP/7zip/Common/OutMemStream.cpp',
            'CPP/7zip/Common/ProgressMt.cpp',
            'CPP/7zip/Common/ProgressUtils.cpp',
            'CPP/7zip/Common/StreamBinder.cpp',
            'CPP/7zip/Common/StreamObjects.cpp',
            'CPP/7zip/Common/StreamUtils.cpp',
            'CPP/7zip/Common/VirtThread.cpp',
            'CPP/7zip/Archive/ArchiveExports.cpp',
            'CPP/7zip/Archive/DllExports2.cpp',
            'CPP/7zip/Archive/ApmHandler.cpp',
            'CPP/7zip/Archive/ArjHandler.cpp',
            'CPP/7zip/Archive/Bz2Handler.cpp',
            'CPP/7zip/Archive/CpioHandler.cpp',
            'CPP/7zip/Archive/CramfsHandler.cpp',
            'CPP/7zip/Archive/DebHandler.cpp',
            'CPP/7zip/Archive/DeflateProps.cpp',
            'CPP/7zip/Archive/DmgHandler.cpp',
            'CPP/7zip/Archive/ElfHandler.cpp',
            'CPP/7zip/Archive/FatHandler.cpp',
            'CPP/7zip/Archive/FlvHandler.cpp',
            'CPP/7zip/Archive/GzHandler.cpp',
            'CPP/7zip/Archive/LzhHandler.cpp',
            'CPP/7zip/Archive/LzmaHandler.cpp',
            'CPP/7zip/Archive/MachoHandler.cpp',
            'CPP/7zip/Archive/MbrHandler.cpp',
            'CPP/7zip/Archive/MslzHandler.cpp',
            'CPP/7zip/Archive/MubHandler.cpp',
            'CPP/7zip/Archive/NtfsHandler.cpp',
            'CPP/7zip/Archive/PeHandler.cpp',
            'CPP/7zip/Archive/PpmdHandler.cpp',
            'CPP/7zip/Archive/RpmHandler.cpp',
            'CPP/7zip/Archive/SplitHandler.cpp',
            'CPP/7zip/Archive/SquashfsHandler.cpp',
            'CPP/7zip/Archive/SwfHandler.cpp',
            'CPP/7zip/Archive/VhdHandler.cpp',
            'CPP/7zip/Archive/XarHandler.cpp',
            'CPP/7zip/Archive/XzHandler.cpp',
            'CPP/7zip/Archive/ZHandler.cpp',
            'CPP/7zip/Archive/Common/CoderMixer2.cpp',
            'CPP/7zip/Archive/Common/CoderMixer2MT.cpp',
            'CPP/7zip/Archive/Common/CrossThreadProgress.cpp',
            'CPP/7zip/Archive/Common/DummyOutStream.cpp',
            'CPP/7zip/Archive/Common/FindSignature.cpp',
            'CPP/7zip/Archive/Common/InStreamWithCRC.cpp',
            'CPP/7zip/Archive/Common/ItemNameUtils.cpp',
            'CPP/7zip/Archive/Common/MultiStream.cpp',
            'CPP/7zip/Archive/Common/OutStreamWithCRC.cpp',
            'CPP/7zip/Archive/Common/OutStreamWithSha1.cpp',
            'CPP/7zip/Archive/Common/HandlerOut.cpp',
            'CPP/7zip/Archive/Common/ParseProperties.cpp',
            'CPP/7zip/Archive/7z/7zCompressionMode.cpp',
            'CPP/7zip/Archive/7z/7zDecode.cpp',
            'CPP/7zip/Archive/7z/7zEncode.cpp',
            'CPP/7zip/Archive/7z/7zExtract.cpp',
            'CPP/7zip/Archive/7z/7zFolderInStream.cpp',
            'CPP/7zip/Archive/7z/7zFolderOutStream.cpp',
            'CPP/7zip/Archive/7z/7zHandler.cpp',
            'CPP/7zip/Archive/7z/7zHandlerOut.cpp',
            'CPP/7zip/Archive/7z/7zHeader.cpp',
            'CPP/7zip/Archive/7z/7zIn.cpp',
            'CPP/7zip/Archive/7z/7zOut.cpp',
            'CPP/7zip/Archive/7z/7zProperties.cpp',
            'CPP/7zip/Archive/7z/7zSpecStream.cpp',
            'CPP/7zip/Archive/7z/7zUpdate.cpp',
            'CPP/7zip/Archive/7z/7zRegister.cpp',
            'CPP/7zip/Archive/Cab/CabBlockInStream.cpp',
            'CPP/7zip/Archive/Cab/CabHandler.cpp',
            'CPP/7zip/Archive/Cab/CabHeader.cpp',
            'CPP/7zip/Archive/Cab/CabIn.cpp',
            'CPP/7zip/Archive/Cab/CabRegister.cpp',
            'CPP/7zip/Archive/Chm/ChmHandler.cpp',
            'CPP/7zip/Archive/Chm/ChmHeader.cpp',
            'CPP/7zip/Archive/Chm/ChmIn.cpp',
            'CPP/7zip/Archive/Chm/ChmRegister.cpp',
            'CPP/7zip/Archive/Com/ComHandler.cpp',
            'CPP/7zip/Archive/Com/ComIn.cpp',
            'CPP/7zip/Archive/Com/ComRegister.cpp',
            'CPP/7zip/Archive/Hfs/HfsHandler.cpp',
            'CPP/7zip/Archive/Hfs/HfsIn.cpp',
            'CPP/7zip/Archive/Hfs/HfsRegister.cpp',
            'CPP/7zip/Archive/Iso/IsoHandler.cpp',
            'CPP/7zip/Archive/Iso/IsoHeader.cpp',
            'CPP/7zip/Archive/Iso/IsoIn.cpp',
            'CPP/7zip/Archive/Iso/IsoRegister.cpp',
            'CPP/7zip/Archive/Nsis/NsisDecode.cpp',
            'CPP/7zip/Archive/Nsis/NsisHandler.cpp',
            'CPP/7zip/Archive/Nsis/NsisIn.cpp',
            'CPP/7zip/Archive/Nsis/NsisRegister.cpp',
            'CPP/7zip/Archive/Rar/RarHandler.cpp',
            'CPP/7zip/Archive/Rar/RarHeader.cpp',
            'CPP/7zip/Archive/Rar/RarIn.cpp',
            'CPP/7zip/Archive/Rar/RarItem.cpp',
            'CPP/7zip/Archive/Rar/RarVolumeInStream.cpp',
            'CPP/7zip/Archive/Rar/RarRegister.cpp',
            'CPP/7zip/Archive/Tar/TarHandler.cpp',
            'CPP/7zip/Archive/Tar/TarHandlerOut.cpp',
            'CPP/7zip/Archive/Tar/TarHeader.cpp',
            'CPP/7zip/Archive/Tar/TarIn.cpp',
            'CPP/7zip/Archive/Tar/TarOut.cpp',
            'CPP/7zip/Archive/Tar/TarRegister.cpp',
            'CPP/7zip/Archive/Tar/TarUpdate.cpp',
            'CPP/7zip/Archive/Udf/UdfHandler.cpp',
            'CPP/7zip/Archive/Udf/UdfIn.cpp',
            'CPP/7zip/Archive/Udf/UdfRegister.cpp',
            'CPP/7zip/Archive/Wim/WimHandler.cpp',
            'CPP/7zip/Archive/Wim/WimHandlerOut.cpp',
            'CPP/7zip/Archive/Wim/WimIn.cpp',
            'CPP/7zip/Archive/Wim/WimRegister.cpp',
            'CPP/7zip/Archive/Zip/ZipAddCommon.cpp',
            'CPP/7zip/Archive/Zip/ZipHandler.cpp',
            'CPP/7zip/Archive/Zip/ZipHandlerOut.cpp',
            'CPP/7zip/Archive/Zip/ZipHeader.cpp',
            'CPP/7zip/Archive/Zip/ZipIn.cpp',
            'CPP/7zip/Archive/Zip/ZipItem.cpp',
            'CPP/7zip/Archive/Zip/ZipOut.cpp',
            'CPP/7zip/Archive/Zip/ZipUpdate.cpp',
            'CPP/7zip/Archive/Zip/ZipRegister.cpp',
            'CPP/7zip/Compress/CodecExports.cpp',
            'CPP/7zip/Compress/ArjDecoder1.cpp',
            'CPP/7zip/Compress/ArjDecoder2.cpp',
            'CPP/7zip/Compress/Bcj2Coder.cpp',
            'CPP/7zip/Compress/Bcj2Register.cpp',
            'CPP/7zip/Compress/BcjCoder.cpp',
            'CPP/7zip/Compress/BcjRegister.cpp',
            'CPP/7zip/Compress/BitlDecoder.cpp',
            'CPP/7zip/Compress/BranchCoder.cpp',
            'CPP/7zip/Compress/BranchMisc.cpp',
            'CPP/7zip/Compress/BranchRegister.cpp',
            'CPP/7zip/Compress/ByteSwap.cpp',
            'CPP/7zip/Compress/BZip2Crc.cpp',
            'CPP/7zip/Compress/BZip2Decoder.cpp',
            'CPP/7zip/Compress/BZip2Encoder.cpp',
            'CPP/7zip/Compress/BZip2Register.cpp',
            'CPP/7zip/Compress/CopyCoder.cpp',
            'CPP/7zip/Compress/CopyRegister.cpp',
            'CPP/7zip/Compress/Deflate64Register.cpp',
            'CPP/7zip/Compress/DeflateDecoder.cpp',
            'CPP/7zip/Compress/DeflateEncoder.cpp',
            'CPP/7zip/Compress/DeflateRegister.cpp',
            'CPP/7zip/Compress/DeltaFilter.cpp',
            'CPP/7zip/Compress/Lzma2Decoder.cpp',
            'CPP/7zip/Compress/Lzma2Encoder.cpp',
            'CPP/7zip/Compress/Lzma2Register.cpp',
            'CPP/7zip/Compress/ImplodeDecoder.cpp',
            'CPP/7zip/Compress/ImplodeHuffmanDecoder.cpp',
            'CPP/7zip/Compress/LzhDecoder.cpp',
            'CPP/7zip/Compress/LzmaDecoder.cpp',
            'CPP/7zip/Compress/LzmaEncoder.cpp',
            'CPP/7zip/Compress/LzmaRegister.cpp',
            'CPP/7zip/Compress/LzOutWindow.cpp',
            'CPP/7zip/Compress/Lzx86Converter.cpp',
            'CPP/7zip/Compress/LzxDecoder.cpp',
            'CPP/7zip/Compress/PpmdDecoder.cpp',
            'CPP/7zip/Compress/PpmdEncoder.cpp',
            'CPP/7zip/Compress/PpmdRegister.cpp',
            'CPP/7zip/Compress/PpmdZip.cpp',
            'CPP/7zip/Compress/QuantumDecoder.cpp',
            'CPP/7zip/Compress/ShrinkDecoder.cpp',
            'CPP/7zip/Compress/ZlibDecoder.cpp',
            'CPP/7zip/Compress/ZlibEncoder.cpp',
            'CPP/7zip/Compress/ZDecoder.cpp',
            'CPP/7zip/Crypto/7zAes.cpp',
            'CPP/7zip/Crypto/7zAesRegister.cpp',
            'CPP/7zip/Crypto/HmacSha1.cpp',
            'CPP/7zip/Crypto/MyAes.cpp',
            'CPP/7zip/Crypto/Pbkdf2HmacSha1.cpp',
            'CPP/7zip/Crypto/RandGen.cpp',
            'CPP/7zip/Crypto/Sha1.cpp',
            'CPP/7zip/Crypto/WzAes.cpp',
            'CPP/7zip/Crypto/Rar20Crypto.cpp',
            'CPP/7zip/Crypto/RarAes.cpp',
            'CPP/7zip/Crypto/ZipCrypto.cpp',
            'CPP/7zip/Crypto/ZipStrong.cpp',
            'C/7zBuf2.c',
            'C/7zStream.c',
            'C/Aes.c',
            'C/Alloc.c',
            'C/Bra.c',
            'C/Bra86.c',
            'C/BraIA64.c',
            'C/BwtSort.c',
            'C/Delta.c',
            'C/HuffEnc.c',
            'C/LzFind.c',
            'C/LzFindMt.c',
            'C/Lzma2Dec.c',
            'C/Lzma2Enc.c',
            'C/LzmaDec.c',
            'C/LzmaEnc.c',
            'C/MtCoder.c',
            'C/Ppmd7.c',
            'C/Ppmd7Dec.c',
            'C/Ppmd7Enc.c',
            'C/Ppmd8.c',
            'C/Ppmd8Dec.c',
            'C/Ppmd8Enc.c',
            'C/Sha256.c',
            'C/Sort.c',
            'C/Xz.c',
            'C/XzCrc64.c',
            'C/XzDec.c',
            'C/XzEnc.c',
            'C/XzIn.c',
            'C/7zCrc.c',
            'C/7zCrcOpt.c',
            'C/Threads.c',
        ]
    ],
)

ffi._apply_windows_unicode(verify_kwargs)
ffi.verifier = Verifier(ffi, SOURCE, **verify_kwargs)

# Patch the Verifier() instance to prevent CFFI from compiling the module
ffi.verifier.compile_module = _compile_module
ffi.verifier._compile_module = _compile_module

_lib7zip = LazyRawLib7zip(ffi)
