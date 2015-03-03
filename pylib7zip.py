from cffi import FFI
ffi = FFI()

with open("windowsdefs.h") as f:
    ffi.cdef(f.read())

ffi.cdef("""
const GUID IID_IInArchive;

enum {
  kpidNoProperty = 0,
  kpidMainSubfile = 1,
  kpidHandlerItemIndex = 2,
  kpidPath,
  kpidName,
  kpidExtension,
  kpidIsDir,
  kpidSize,
  kpidPackSize,
  kpidAttrib,
  kpidCTime,
  kpidATime,
  kpidMTime,
  kpidSolid,
  kpidCommented,
  kpidEncrypted,
  kpidSplitBefore,
  kpidSplitAfter,
  kpidDictionarySize,
  kpidCRC,
  kpidType,
  kpidIsAnti,
  kpidMethod,
  kpidHostOS,
  kpidFileSystem,
  kpidUser,
  kpidGroup,
  kpidBlock,
  kpidComment,
  kpidPosition,
  kpidPrefix,
  kpidNumSubDirs,
  kpidNumSubFiles,
  kpidUnpackVer,
  kpidVolume,
  kpidIsVolume,
  kpidOffset,
  kpidLinks,
  kpidNumBlocks,
  kpidNumVolumes,
  kpidTimeType,
  kpidBit64,
  kpidBigEndian,
  kpidCpu,
  kpidPhySize,
  kpidHeadersSize,
  kpidChecksum,
  kpidCharacts,
  kpidVa,
  kpidId,
  kpidShortName,
  kpidCreatorApp,
  kpidSectorSize,
  kpidPosixAttrib,
  kpidLink,
  kpidError,

  kpidTotalSize = 0x1100,
  kpidFreeSpace,
  kpidClusterSize,
  kpidVolumeName,

  kpidLocalName = 0x1200,
  kpidProvider,

  kpidUserDefined = 0x10000
};

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
    _get_password_callback get_password_callback, /* optional - takes precedence over password */
    _set_total_callback set_total_callback, /* optional */
    _set_completed_callback set_completed_callback /* optional */);

HRESULT archive_get_num_items(IInArchive* archive, uint32_t* num_items);
HRESULT archive_get_item_property_pvar(
    IInArchive* archive, uint32_t index, uint32_t prop, PROPVARIANT* pvar);

HRESULT archive_close(IInArchive*);
""")

P7ZIPSOURCE='p7zip_9.20.1'
clib7zip = ffi.verify(
    """
    #include "windowsdefs.h"
    #include "clib7zip.h"
    """,
    #modulename='clib7zip',
    sources=[
        'clib7zip.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyWindows.cpp',
        P7ZIPSOURCE + '/CPP/Windows/PropVariant.cpp',
    ],
    #library_dirs=['.'],
    libraries=['dl'],
    include_dirs=[
        '.', P7ZIPSOURCE + '/CPP',
        P7ZIPSOURCE + '/CPP/7zip/UI/Client7z',
        P7ZIPSOURCE + '/CPP/myWindows',
        P7ZIPSOURCE + '/CPP/include_windows',
    ],
    define_macros=[
        ('_FILE_OFFSET_BITS', '64'),
        ('_LARGEFILE_SOURCE',),
        ('UNICODE', ),
        ('_UNICODE', ),
    ],
)

ffi2 = FFI()
with open("windowsdefs.h") as f:
    ffi2.cdef(f.read())

ffi2.cdef("""
uint32_t GetNumberOfFormats(uint32_t*);
uint32_t GetNumberOfMethods(uint32_t *);
uint32_t GetMethodProperty(uint32_t index, uint32_t propID, void * value);
uint32_t GetHandlerProperty2(uint32_t, uint32_t propID, void *);
uint32_t CreateObject(GUID *, GUID *, void **);
""")

def RNOK(hresult):
    if hresult != clib7zip.S_OK:
        raise Exception("HRESULT ERROR=%x" % hresult)

def main():
    lib7zip = ffi2.dlopen("/usr/lib/p7zip/7z.so")
    pvar = ffi.gc(clib7zip.create_propvariant(), clib7zip.destroy_propvariant)
    with open("abc.7z", "rb") as f:
        print("Creating stream...")
        stream = clib7zip.create_instream_from_file(f);
        assert stream != ffi.NULL
        print("...Created")
        print("Creating archive...")
        num_items = ffi.new("uint32_t*")
        RNOK(lib7zip.GetNumberOfFormats(num_items))
        print("num_items=%d" % num_items[0])
        for i in range(num_items[0]):
            print("i=%d" % i)
            RNOK(lib7zip.GetHandlerProperty2(i, clib7zip.NArchive_kName, pvar))
            print("7z=%s" % ffi.string(pvar.bstrVal))
            if ffi.string(pvar.bstrVal) == "7z":
                print("found it")
                break

        print("Creating Archive Object...")
        RNOK(lib7zip.GetHandlerProperty2(i, clib7zip.NArchive_kClassID, pvar))
        archive_p = ffi.new("void**")

        RNOK(lib7zip.CreateObject(
            ffi2.cast("GUID*", pvar.puuid),
            ffi2.cast("GUID*", ffi2.addressof(clib7zip.IID_IInArchive)),
            archive_p,
        ))
        archive = ffi.cast("IInArchive*", archive_p[0])
        assert archive != ffi.NULL
        print("...Created")
        print("Opening...");
        clib7zip.archive_open(archive, stream, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL);
        print("...Opened");
        RNOK(clib7zip.archive_get_num_items(archive, num_items))
        print("num_items=%d" % num_items[0])
        for i in range(num_items[0]):
            print("i=%d" % i)
            RNOK(clib7zip.archive_get_item_property_pvar(archive, i, clib7zip.kpidPath, pvar))
            assert pvar.vt == clib7zip.VT_BSTR
            print("path=%s" % ffi.string(pvar.bstrVal))
        print("Closing...")
        RNOK(clib7zip.archive_close(archive))
        print("...Closing")

if __name__ == '__main__':
    main()
