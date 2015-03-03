from cffi import FFI
ffi = FFI()
ffi.cdef("""
enum {
    S_OK = 0
};

typedef uint32_t HRESULT;

typedef enum {
    VT_EMPTY = 0,
    VT_BSTR = 8,
    VT_UI4 = 19
} VARTYPE;

typedef struct {
    VARTYPE vt;
    uint8_t wReserved1;
    uint8_t wReserved2;
    uint8_t wReserved3;
    union {
        uint64_t ulVal;
        wchar_t* bstrVal;
    };
} PROPVARIANT;

typedef struct CLIB7ZIP CLIB7ZIP;
CLIB7ZIP* init_clib7zip(const char* lib_path);
void teardown_clib7zip(CLIB7ZIP* lib);

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
IInArchive* create_archive(const wchar_t* type);
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
HRESULT archive_get_item_property_str(
    IInArchive* archive, uint32_t index, uint32_t prop, wchar_t buf[], size_t buf_size);
HRESULT archive_get_item_property_uint64(
    IInArchive* archive, uint32_t index, uint32_t prop_id, uint64_t* out);

HRESULT archive_close(IInArchive*);
""")

P7ZIPSOURCE='p7zip_9.20.1'
clib7zip = ffi.verify(
    '#include "clib7zip.h"',
    #modulename='clib7zip',
    sources=[
        'clib7zip.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyWindows.cpp',
        P7ZIPSOURCE + '/CPP/Windows/PropVariant.cpp',
    ],
    libraries=['dl'],
    include_dirs=[
        '.',
        P7ZIPSOURCE + '/CPP',
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

lib7zip = clib7zip.init_clib7zip(ffi.NULL)
with open("abc.7z", "rb") as f:
    print("Creating stream...")
    stream = clib7zip.create_instream_from_file(f);
    assert stream != ffi.NULL
    print("...Created")
    print("Creating archive...")
    archive = clib7zip.create_archive("7z")
    assert archive != ffi.NULL
    print("...Created")
    print("Opening...");
    clib7zip.archive_open(archive, stream, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL);
    print("...Opened");

clib7zip.teardown_clib7zip(lib7zip)
