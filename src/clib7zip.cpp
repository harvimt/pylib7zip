#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
#include <stdint.h>
#include <dlfcn.h>
#include <errno.h>

#include "StdAfx.h"
//#include "Common/MyInitGuid.h"
#include "Windows/PropVariant.h"

#include "Common/MyCom.h"

#include "7zip/IStream.h"
#include "7zip/Archive/IArchive.h"
#include "7zip/IPassword.h"

#include "clib7zip.h"

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

PROPVARIANT* create_propvariant(){
    return new NWindows::NCOM::CPropVariant();
}
void destroy_propvariant(PROPVARIANT* pvar){
    ((NWindows::NCOM::CPropVariant*) pvar)->Clear();
    delete pvar;
}

IInStream* create_instream_from_file(FILE* file){ return (IInStream*)(new CInFileStream(file)); }

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
