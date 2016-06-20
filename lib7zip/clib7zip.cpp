#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
#include <stdint.h>
//#include <dlfcn.h>
#include <errno.h>
#include <stdarg.h>
#include <basetyps.h>

#include "StdAfx.h"
#include "Windows/PropVariant.h"

#include "Common/MyCom.h"

#include "7zip/IStream.h"
#include "7zip/Archive/IArchive.h"
#include "7zip/IPassword.h"

#include "clib7zip.h"

#ifdef WIN32
#include <io.h>
#else
#include <unistd.h>
#endif

static void (*log_debug_cb)(const char*) = NULL;

void set_logger_cb(void(*cb)(const char*)) {
    log_debug_cb = cb;
}
STDAPI GetNumberOfFormats(uint32_t*);
STDAPI GetNumberOfMethods(uint32_t *);
STDAPI GetMethodProperty(uint32_t index, uint32_t propID, PROPVARIANT * value);
STDAPI GetHandlerProperty2(uint32_t, uint32_t propID, PROPVARIANT *);
STDAPI CreateObject(const GUID *, const GUID *, void **);

HRESULT _GetNumberOfFormats(uint32_t* num_formats){ return GetNumberOfFormats(num_formats); }
HRESULT _GetNumberOfMethods(uint32_t* num_methods){ return GetNumberOfMethods(num_methods);}
HRESULT _GetMethodProperty(uint32_t index, uint32_t propID, PROPVARIANT * value){ return GetMethodProperty(index, propID, value);}
HRESULT _GetHandlerProperty2(uint32_t index, uint32_t propID, PROPVARIANT * value){ return GetHandlerProperty2(index, propID, value);}
HRESULT _CreateObject(const GUID * _1, const GUID * _2, void ** _3){return CreateObject(_1, _2, _3);}

static inline void LOG_DEBUG(const char* fmt, ...){
    char buffer[256];
    va_list args;
    va_start(args, fmt);
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);
    if (log_debug_cb == NULL){
        fprintf(stderr, "%s\n", buffer);
    } else {
        log_debug_cb(buffer);
    }
}

class CFileStream:
  public IInStream,
  public IOutStream,
  public IStreamGetSize,
  public CMyUnknownImp
{
public:
  CFileStream(FILE* file_ptr_in) : file_ptr(file_ptr_in) {}
  virtual ~CFileStream() {fclose(file_ptr);}
  MY_UNKNOWN_IMP2(IInStream, IStreamGetSize)

  STDMETHOD(Read)(void *data, UInt32 size, UInt32 *processedSize);
  STDMETHOD(Write)(const void *data, UInt32 size, UInt32 *processedSize);
  STDMETHOD(Seek)(Int64 offset, UInt32 seekOrigin, UInt64 *newPosition);

  STDMETHOD(GetSize)(UInt64 *size);
  STDMETHOD(SetSize)(UINT64 size);
  
private:
  FILE* file_ptr;
};

STDMETHODIMP CFileStream::Read (void *data, UInt32 size, UInt32 *processedSize) {
    LOG_DEBUG("FileStream::Read");
    if(processedSize !=  NULL){
        *processedSize = static_cast<uint32_t>(fread(data, sizeof(uint8_t), size, file_ptr));
    }else{
        fread(data, sizeof(uint8_t), size, file_ptr);
    }
    return S_OK;
}

STDMETHODIMP CFileStream::Write (const void *data, UInt32 size, UInt32 *processedSize) {
    LOG_DEBUG("FileStream::Write");
    if(processedSize !=  NULL){
        *processedSize = static_cast<uint32_t>(fwrite(data, sizeof(uint8_t), size, file_ptr));
    }else{
        fwrite(data, sizeof(uint8_t), size, file_ptr);
    }
    return S_OK;
}

#ifdef WIN32
#define fseeko64 _fseeki64
#define ftello64 _ftelli64
typedef __int64 off64_t;
#define ftruncate64 _chsize_s
#endif

STDMETHODIMP CFileStream::Seek (Int64 offset, UInt32 seekOrigin, UInt64 *newPosition){
    LOG_DEBUG("CFileStream::Seek(%lld, %u, %p)", offset, seekOrigin, newPosition);
    if (file_ptr == NULL){ LOG_DEBUG("file_ptr is NULL"); return E_ABORT; };
    if(fseeko64(file_ptr, offset, seekOrigin) == -1){
        perror("fseek failed");
        return E_ABORT;
    }
    if(newPosition != NULL){
        *newPosition = ftello64(file_ptr);
    }
    return S_OK;
}

STDMETHODIMP CFileStream::GetSize(UInt64 *size){
    LOG_DEBUG("CFileStream::GetSize(%p)", size);
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

STDMETHODIMP CFileStream::SetSize(UInt64 size){
    LOG_DEBUG("CFileStream::SetSize(%p)", size);
	ftruncate64(_fileno(file_ptr), size);
	//FIXME handle errors?
    return S_OK;
}

IInStream* create_instream_from_file(FILE* file){ return (IInStream*)(new CFileStream(file)); }
IOutStream* create_outstream_from_file(FILE* file){ return (IOutStream*)(new CFileStream(file)); }

class PyFileStream:
  public IInStream,
  public IOutStream,
  public IStreamGetSize,
  public CMyUnknownImp
{
public:
  PyFileStream(void* py_file_in) : py_file(py_file_in) {}
  virtual ~PyFileStream() {py_file_close(py_file);}
  MY_UNKNOWN_IMP2(IInStream, IStreamGetSize)

  STDMETHOD(Read)(void *data, UInt32 size, UInt32 *processedSize);
  STDMETHOD(Write)(const void *data, UInt32 size, UInt32 *processedSize);
  STDMETHOD(Seek)(Int64 offset, UInt32 seekOrigin, UInt64 *newPosition);

  STDMETHOD(GetSize)(UInt64 *size);
  STDMETHOD(SetSize)(UINT64 size);
  
private:
  void* py_file;
};

STDMETHODIMP PyFileStream::Read (void *data, UInt32 size, UInt32 *processedSize) {
	return py_file_read(py_file, data, size, processedSize);
}

STDMETHODIMP PyFileStream::Write (const void *data, UInt32 size, UInt32 *processedSize) {
	return py_file_write(py_file, data, size, processedSize);
}

STDMETHODIMP PyFileStream::Seek (Int64 offset, UInt32 seekOrigin, UInt64 *newPosition){
	return py_file_seek(py_file, offset, seekOrigin, newPosition);
}

STDMETHODIMP PyFileStream::GetSize(UInt64 *size){
    return py_file_getsize(py_file, size);
}

STDMETHODIMP PyFileStream::SetSize(UInt64 size){
	return py_file_setsize(py_file, size);
}

class CArchiveOpenCallback:
  public IArchiveOpenCallback,
  public ICryptoGetTextPassword,
  public CMyUnknownImp
{
public:
    MY_UNKNOWN_IMP1(ICryptoGetTextPassword)

    CArchiveOpenCallback(
		void* data,
        BSTR password,
        _aopen_get_password_callback p_cb,
        _aopen_set_total_callback t_cb,
		_aopen_set_completed_callback c_cb
    ) :
        data(data),
        user_password(password),
		get_password_callback(p_cb),
        set_total_callback(t_cb),
		set_completed_callback(c_cb)
    {};
	
    STDMETHOD(SetTotal)(const UInt64 *files, const UInt64 *bytes);
    STDMETHOD(SetCompleted)(const UInt64 *files, const UInt64 *bytes);
    STDMETHOD(CryptoGetTextPassword)(BSTR *password);
private:
    void* data;
    wchar_t* user_password;
	_aopen_get_password_callback get_password_callback;
	_aopen_set_total_callback set_total_callback;
	_aopen_set_completed_callback set_completed_callback;
};


STDMETHODIMP CArchiveOpenCallback::SetTotal(const UInt64 * files, const UInt64 * bytes)
{
    LOG_DEBUG("CArchiveOpenCallback::SetTotal");
	//return S_OK;
    //if (set_total_callback == NULL) return S_OK;
    return set_total_callback(data, files, bytes);
}

STDMETHODIMP CArchiveOpenCallback::SetCompleted(const UInt64 * files, const UInt64 * bytes)
{
    LOG_DEBUG("CArchiveOpenCallback::SetCompleted");
    if (set_completed_callback == NULL) return S_OK;
    return set_completed_callback(data, (const uint64_t*)(files), (const uint64_t*)(bytes));
}

STDMETHODIMP CArchiveOpenCallback::CryptoGetTextPassword(BSTR *password)
{
    LOG_DEBUG("CArchiveOpenCallback::CryptoGetTextPassword");
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


HRESULT archive_open(
    IInArchive* archive,
    IInStream* in_stream,
    void* data,
    wchar_t* password,
    _aopen_get_password_callback get_password_callback, /*optional, takes precedence over password */
    _aopen_set_total_callback set_total_callback, /* optional */
    _aopen_set_completed_callback set_completed_callback /* optional */)
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
    if(archive == NULL){ LOG_DEBUG("archive is NULL"); return 0; }; //FIXME
    if(num_items == NULL){ LOG_DEBUG("num_items is NULL"); return 0; }; // FIXME

    HRESULT res = archive->GetNumberOfItems(num_items);
    LOG_DEBUG("-> num_items=%d", *num_items);
    return res;
}

HRESULT archive_get_item_property_pvar(
    IInArchive* archive, uint32_t index, PROPID prop_id, PROPVARIANT* pvar)
{
    //*pvar = create_propvariant();
    if(pvar == NULL){ LOG_DEBUG("pvar is NULL"); return E_ABORT; }; //FIXME
    return archive->GetProperty(index, prop_id, pvar);
}