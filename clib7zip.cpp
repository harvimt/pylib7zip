#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
#include <stdint.h>
#include <dlfcn.h>
#include <errno.h>

#include "StdAfx.h"

#include "Common/IntToString.h"
#include "Common/MyInitGuid.h"
#include "Common/StringConvert.h"

#include "Windows/DLL.h"
//#include "Windows/FileDir.h"
//#include "Windows/FileFind.h"
//#include "Windows/FileName.h"
#include "Windows/NtCheck.h"
#include "Windows/PropVariant.h"
#include "Windows/PropVariantConversions.h"

#include "Common/MyCom.h"
#include "7zip/IStream.h"

//#include "7zip/Common/FileStreams.h"
#include "7zip/Archive/IArchive.h"

#include "7zip/IPassword.h"
#include "7zip/MyVersion.h"
#include "clib7zip.h"

DEFINE_GUID(CLSID_CFormat7z,
  0x23170F69, 0x40C1, 0x278A, 0x10, 0x00, 0x00, 0x01, 0x10, 0x07, 0x00, 0x00);

typedef HRESULT (WINAPI *_GetNumberOfFormats)(uint32_t*);
typedef HRESULT (WINAPI *_GetNumberOfMethods)(uint32_t *);
typedef HRESULT (WINAPI *_GetMethodProperty)(uint32_t index, PROPID propID, PROPVARIANT * value);
typedef HRESULT (WINAPI *_GetHandlerProperty2)(uint32_t, PROPID propID, PROPVARIANT *);
typedef HRESULT (WINAPI *_CreateObject)(const GUID *, const GUID *, void **);

_GetNumberOfFormats GetNumberOfFormats;
_GetNumberOfMethods GetNumberOfMethods;
_GetMethodProperty GetMethodProperty;
_GetHandlerProperty2 GetHandlerProperty2;
_CreateObject CreateObject;

class CInFileStream:
  public IInStream,
  public IStreamGetSize,
  public CMyUnknownImp
{
public:
  CInFileStream(FILE* file_ptr_in) : file_ptr(file_ptr_in) {}
  virtual ~CInFileStream() {}
  MY_UNKNOWN_IMP2(IInStream, IStreamGetSize)

  STDMETHOD(Read)(void *data, UInt32 size, UInt32 *processedSize);
  STDMETHOD(Seek)(Int64 offset, UInt32 seekOrigin, UInt64 *newPosition);

  STDMETHOD(GetSize)(UInt64 *size);
private:
  FILE* file_ptr;
};

STDMETHODIMP CInFileStream::Read (void *data, UInt32 size, UInt32 *processedSize) {
    puts("FileIInStream::Read");
    if(processedSize !=  NULL){
        *processedSize = fread(data, sizeof(uint8_t), size, file_ptr);
    }else{
        fread(data, sizeof(uint8_t), size, file_ptr);
    }
    return S_OK;
}

#if WIN32
#define fseeko64 _fseeki64
#endif

STDMETHODIMP CInFileStream::Seek (Int64 offset, UInt32 seekOrigin, UInt64 *newPosition){
    printf("CFileInStream::Seek(%lld, %u, %p)\n", offset, seekOrigin, newPosition);
    if (file_ptr == NULL){ puts("file_ptr is NULL"); return E_ABORT; };
    if(fseeko64(file_ptr, offset, seekOrigin) == -1){
        perror("fseek failed");
        return E_ABORT;
    }
    if(newPosition != NULL){
        *newPosition = ftello64(file_ptr);
    }
    return S_OK;
}

STDMETHODIMP CInFileStream::GetSize(UInt64 *size){
    printf("CFileInStream::GetSize(%p)\n", size);
    if (size == NULL) { return S_OK; }
    off64_t offset = ftello64(file_ptr);
    if(fseeko64(file_ptr, 0, SEEK_END) == -1){
        perror("fseek failed");
    }
    *size = ftell(file_ptr);
    if(fseeko64(file_ptr, offset, SEEK_SET) == -1){
        perror("fseek failed");
    }
    return S_OK;
}

class CArchiveOpenCallback:
  public IArchiveOpenCallback,
  public ICryptoGetTextPassword,
  public CMyUnknownImp
{
public:
    MY_UNKNOWN_IMP1(ICryptoGetTextPassword)

    CArchiveOpenCallback(void* data, wchar_t* password,
        _get_password_callback p_cb,
        _set_total_callback t_cb, _set_completed_callback c_cb
    ) :
        data(data),
        user_password(password), get_password_callback(p_cb),
        set_total_callback(t_cb), set_completed_callback(c_cb)
    {};

    STDMETHOD(SetTotal)(const UInt64 *files, const UInt64 *bytes);
    STDMETHOD(SetCompleted)(const UInt64 *files, const UInt64 *bytes);

    STDMETHOD(CryptoGetTextPassword)(BSTR *password);
private:
    void* data;
    wchar_t* user_password;
    _get_password_callback get_password_callback;
    _set_total_callback set_total_callback;
    _set_completed_callback set_completed_callback;

};

STDMETHODIMP CArchiveOpenCallback::SetTotal(const UInt64 * files, const UInt64 * bytes)
{
    puts("CArchiveOpenCallback::SetTotal");
    if (set_total_callback == NULL) return S_OK;
    return set_total_callback(data, (const uint64_t*)(files), (const uint64_t*)(bytes));
}

STDMETHODIMP CArchiveOpenCallback::SetCompleted(const UInt64 * files, const UInt64 * bytes)
{
    puts("CArchiveOpenCallback::SetCompleted");
    if (set_completed_callback == NULL) return S_OK;
    return set_completed_callback(data, (const uint64_t*)(files), (const uint64_t*)(bytes));
}

STDMETHODIMP CArchiveOpenCallback::CryptoGetTextPassword(BSTR *password)
{
    puts("CArchiveOpenCallback::CryptoGetTextPassword");
    if (get_password_callback != NULL){
        return get_password_callback(data, password);
    } else if (user_password != NULL && password != NULL){
        *password = user_password;
        return S_OK;
    } else {
        return E_ABORT;
    }
}

typedef struct CLIB7ZIP {
#if WIN32
    HMODULE lib;
#else
    void* lib;
#endif
} CLIB7ZIP;

CLIB7ZIP* init_clib7zip(const char* lib_path){
    puts("Initializing CLIB7ZIP");
    CLIB7ZIP* lib = (CLIB7ZIP*)malloc(sizeof(CLIB7ZIP));
    puts("Malloc Complete");

#if WIN32
#define dlopen_rtld_now LoadLibrary
#define dlsym GetProcAddress
//TODO dlerror
const char *lib_paths[] = {
    "C:\\Program Files\\7-Zip\\7z.dll",
    "C:\\Program Files (x86)\\7-Zip\\7z.dll"
};
#else
#define dlopen_rtld_now(path) dlopen(path, RTLD_NOW)
const char *lib_paths[] = {
    "/usr/lib/p7zip/7z.so"
};
#endif
    if(lib_path){
        printf("Trying to open 7zip library: %s\n", lib_path);
        lib->lib = dlopen_rtld_now(lib_path);
    } else {
        printf("Trying to open 7zip library from a default path\n");
        for(unsigned int i = 0; i < sizeof(lib_paths) / sizeof(char*); i += 1){
            printf("Trying to open 7zip library: %s\n", lib_paths[i]);
            lib->lib = dlopen_rtld_now(lib_paths[i]);
            if(lib->lib != NULL){
                puts("Loaded");
                break;
            }
        }
    }
    if (lib->lib == NULL){
        puts("NULL FAIL"); //FIXME
        return NULL;
    }

    GetNumberOfFormats = (_GetNumberOfFormats) dlsym(lib->lib, "GetNumberOfFormats");
    if(GetNumberOfFormats == NULL){
        puts("NULL FAIL"); // FIXME
        return NULL;
    }

    GetHandlerProperty2 = (_GetHandlerProperty2) dlsym(lib->lib, "GetHandlerProperty2");
    if(GetHandlerProperty2 == NULL){
        puts("NULL FAIL"); // FIXME
        return NULL;
    }

    CreateObject = (_CreateObject) dlsym(lib->lib, "CreateObject");
    if(CreateObject == NULL){
        puts("NULL FAIL"); // FIXME
        return NULL;
    }
    return lib;
}

void teardown_clib7zip(CLIB7ZIP* lib){
    dlclose(lib->lib);
    free(lib);
}

PROPVARIANT* create_propvariant(){
    return new NWindows::NCOM::CPropVariant();
}
void destroy_propvariant(PROPVARIANT* pvar){
    ((NWindows::NCOM::CPropVariant*) pvar)->Clear();
    delete pvar;
}

IInStream* create_instream_from_file(FILE* file){ return (IInStream*)(new CInFileStream(file)); } IInArchive* create_archive(const wchar_t* type) {
    printf("Creating archive of type %ls\n", type);
    uint32_t num_formats;
    GetNumberOfFormats(&num_formats);
    printf("num_formats=%d\n", num_formats);
    HRESULT res;
    GUID* archive_guid = NULL;
    IInArchive* archive;
    for (unsigned int i = 0; i < num_formats; i += 1){
        printf("i=%d\n", i);
        NWindows::NCOM::CPropVariant prop;
        res = GetHandlerProperty2(i, NArchive::kName, &prop);
        if(res != S_OK){
            puts("S_OK, error");
            return NULL;
        }
        if(prop.vt != VT_BSTR){
            puts("vt != VT_BSTR");
            return NULL;
        }
        //printf("name=%ls\n", prop.bstrVal);
        if(wcscmp(prop.bstrVal, type) == 0){
            res = GetHandlerProperty2(i, NArchive::kClassID, &prop);
            archive_guid = (GUID*) prop.bstrVal;
        }
        if(archive_guid == NULL){
            puts("NULL ERROR");
            return NULL;
        }
        res = CreateObject(archive_guid, &IID_IInArchive, (void**)(&archive));
        if (res != S_OK){
            puts("S_OK ERROR");
            return NULL;
        }
        return archive;
    }
    fprintf(stderr, "Archive type %ls not found\n", type);
    return NULL;
}

HRESULT archive_open(
    IInArchive* archive,
    IInStream* in_stream,
    void* data,
    wchar_t* password,
    _get_password_callback get_password_callback, /*optional, takes precedence over password */
    _set_total_callback set_total_callback, /* optional */
    _set_completed_callback set_completed_callback /* optional */)
{
    if (archive == NULL){ return E_ABORT; }
    CArchiveOpenCallback* open_callback = new CArchiveOpenCallback(
        data,
        password,
        get_password_callback,
        set_total_callback,
        set_completed_callback);

    const UInt64 maxCheckStartPosition = 1 << 22;
    archive->Open(in_stream, &maxCheckStartPosition, open_callback);
    return S_OK;
}

HRESULT archive_close(IInArchive* archive){
    return archive->Close();
}

void archive_release(IInArchive* archive){
    delete archive;
}

HRESULT archive_get_num_items(IInArchive* archive, uint32_t* num_items) {
    if(archive == NULL){ puts("archive is NULL"); return 0; }; //FIXME
    if(num_items == NULL){ puts("num_items is NULL"); return 0; }; // FIXME

    HRESULT res = archive->GetNumberOfItems(num_items);
    printf("-> num_items=%d\n", *num_items);
    return res;
}

HRESULT archive_get_item_property_pvar(
    IInArchive* archive, uint32_t index, PROPID prop_id, PROPVARIANT* pvar)
{
    //*pvar = create_propvariant();
    if(pvar == NULL){ puts("pvar is NULL"); return E_ABORT; }; //FIXME
    return archive->GetProperty(index, prop_id, pvar);
}

HRESULT archive_get_item_property_str(
    IInArchive* archive, uint32_t index, PROPID prop_id, wchar_t buf[], size_t buf_size)
{
    HRESULT res;
    if(buf == NULL){ puts("buf is NULL"); return E_ABORT; }; //FIXME
    NWindows::NCOM::CPropVariant prop;
    res = archive->GetProperty(index, prop_id, &prop);
    if (res != S_OK) {
        printf("IInArchive::GetProperty() gave error code=%x\n", res);
        return res;
    };
    if (prop.vt != VT_BSTR){ puts("prop.vt != VT_BSTR"); return E_ABORT; }; //FIXME
    buf[buf_size] = L'\0';
    wcsncpy(buf, prop.bstrVal, buf_size);
    if (buf[buf_size] != L'\0'){
        puts("Buffer overrun");
        return E_ABORT;
    }
    return S_OK;
}

HRESULT archive_get_item_property_uint64(
    IInArchive* archive, uint32_t index, PROPID prop_id, uint64_t* out){
    HRESULT res;
    if(out == NULL){ puts("out is NULL"); return E_ABORT; }; //FIXME
    NWindows::NCOM::CPropVariant prop;
    res = archive->GetProperty(index, prop_id, &prop);
    if (res != S_OK) {
        printf("IInArchive::GetProperty() gave error code=%x\n", res);
        return res;
    };
    if(prop.vt != VT_UI4){ puts("prop.vt != VT_UI4"); return E_ABORT; }; //FIXME
    *out = prop.ulVal;
    return S_OK;
}
