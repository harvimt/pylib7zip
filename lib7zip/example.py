import time, sys
import uuid
from collections import namedtuple

from cffi import FFI
ffi = FFI()

ffi.cdef()

ffi.cdef("""

typedef unsigned int UInt32;
typedef ULONG PROPID;

typedef struct {
    unsigned long  Data1;
    unsigned short Data2;
    unsigned short Data3;
    unsigned char  Data4[ 8 ];
} GUID;

typedef struct {
	unsigned short status;
	unsigned short code;
} HRESULT;

typedef struct {
	HRESULT (*QueryInterface) (void*, GUID*, void**);
} IUnknown_vtable;

typedef struct {
	IUnknown_vtable* vtable;
} IUnknown;


HRESULT GetMethodProperty(UInt32 index, PROPID propID, PROPVARIANT * value);
HRESULT GetNumberOfMethods(UInt32 * numMethods);
HRESULT GetNumberOfFormats(UInt32 * numFormats);
/*HRESULT GetHandlerProperty(PROPID propID, PROPVARIANT * value);*/
HRESULT GetHandlerProperty2(UInt32 index, PROPID propID, PROPVARIANT * value);
HRESULT CreateObject(const GUID * clsID, const GUID * iid, void ** outObject);
/*HRESULT SetLargePageMode();*/

void* create_c7zInSt_Filename(const char* filename);
void free_C7ZipInStream(void* stream);

int wprintf(const wchar_t*, ...);
""")

## Magic Numbers ##
S_OK = 0
VT_EMPTY = 0
VT_NULL = 1
VT_BSTR = 8
VT_UI8 = 21

class FormatProps:
	kName = 0
	kClassID = 1
	kExtension = 2

class MethodProps:
	kID = 0
	kName = 1
	kDecoder = 2
	kEncoder = 3 
	kInStreams = 4
	kOutStreams = 5
	kDescription = 6
	kDecoderIsAssigned = 7
	kEncoderIsAssigned = 8

dll7z = ffi.dlopen('7z')
c7z = ffi.dlopen('c7zip')

tmp_pvar = ffi.new("PROPVARIANT*")


SCOPE_FORMAT = object()
SCOPE_METHOD = object()

def get_prop(i, prop, type, scope):
	if scope is SCOPE_FORMAT:
		fn = dll7z.GetHandlerProperty2
		prop = getattr(FormatProps, prop)
	elif scope is SCOPE_METHOD:
		fn = dll7z.GetMethodProperty
		prop = getattr(MethodProps, prop)
	else:
		raise TypeError

	assert fn(i, prop, tmp_pvar).status == S_OK
	assert tmp_pvar != ffi.NULL
	
	if tmp_pvar[0].vt in (VT_EMPTY, VT_NULL):
		return None
		
	if tmp_pvar[0].vt != type:
		raise TypeError('expected %d got %d' % (type, tmp_pvar[0].vt))
	

	# arguably bad, since I'm reusing the same tmp_pvar all the time
	# but it usually gets cast to something else before get_prop is called again
	return tmp_pvar  

def get_string_prop(i, prop, scope):
	tmp_pvar = get_prop(i, prop, VT_BSTR, scope)
	if tmp_pvar is None:
		return ''
	return ffi.string(tmp_pvar[0].bstrVal)

def get_classid(i, prop, scope):
	tmp_pvar = get_prop(i, prop, VT_BSTR, scope)
	if tmp_pvar is None: return None
	return uuid.UUID(bytes_le=b''.join(ffi.cast('char[16]', tmp_pvar[0].pcVal)))

_remember = []
def uu2guid(uu):
	guid = ffi.new('GUID*')
	data = ffi.new('uint8_t[16]', uu.bytes_le)
	_remember.append(data)
	return ffi.cast('GUID*', data)

Format = namedtuple('Format', ('classid', 'extensions', 'index'))
def get_format_info():
	num_formats = ffi.new("UInt32*")
	assert dll7z.GetNumberOfFormats(num_formats).status == S_OK
	assert num_formats != ffi.NULL

	return {
		get_string_prop(i, 'kName', SCOPE_FORMAT): Format(
			classid=get_classid(i, 'kClassID', SCOPE_FORMAT),
			extensions=tuple(get_string_prop(i, 'kExtension', SCOPE_FORMAT).split()),
			index=i,
		)
		for i in range(num_formats[0])
	}

FORMATS = get_format_info()

Method = namedtuple('Method', ('method_id', 'description', 'encoder', 'decoder',))
def get_method_info():
	num_methods = ffi.new("UInt32*")
	assert dll7z.GetNumberOfMethods(num_methods).status == S_OK
	assert num_methods != ffi.NULL
	
	return {
		get_string_prop(i, 'kName', SCOPE_METHOD): Method(
			method_id=get_prop(i, 'kID', VT_UI8, SCOPE_METHOD)[0].uhVal,
			description=get_string_prop(i, 'kDescription', SCOPE_METHOD),
			encoder=get_classid(i, 'kEncoder', SCOPE_METHOD),
			decoder=get_classid(i, 'kDecoder', SCOPE_METHOD),
		)
		for i in range(num_methods[0])
	}

METHODS = get_method_info()

'''
extern "C" const GUID  IID_IInArchive; struct IInArchive: public IUnknown
{
	 virtual __declspec(nothrow) HRESULT __stdcall Open(IInStream *stream, const UInt64 *maxCheckStartPosition, IArchiveOpenCallback *openArchiveCallback) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall Close() = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetNumberOfItems(UInt32 *numItems) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetProperty(UInt32 index, PROPID propID, PROPVARIANT *value) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall Extract(const UInt32* indices, UInt32 numItems, Int32 testMode, IArchiveExtractCallback *extractCallback) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetArchiveProperty(PROPID propID, PROPVARIANT *value) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetNumberOfProperties(UInt32 *numProperties) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetPropertyInfo(UInt32 index, BSTR *name, PROPID *propID, VARTYPE *varType) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetNumberOfArchiveProperties(UInt32 *numProperties) = 0;
	 virtual __declspec(nothrow) HRESULT __stdcall GetArchivePropertyInfo(UInt32 index, BSTR *name, PROPID *propID, VARTYPE *varType) = 0;
};
'''

ffi.cdef("""

""")

def open_archive(filename):
	classid = uu2guid(FORMATS['7z'].classid)
	_archive = ffi.new('void**')
	archive = ffi.cast('IUnknown**', _archive)
	stream = c7z.create_c7zInSt_Filename(filename)
	
	assert dll7z.CreateObject(classid, uu2guid(IInArchive), _archive).status == S_OK
	assert archive[0] != ffi.NULL
	
	qresult = ffi.new('void**')
	
	archive[0].vtable.QueryInterface(archive[0], uu2guid(IUnknown), qresult)
	assert qresult[0] != ffi.NULL

	return archive, qresult
	
def deinit():
	del METHODS
	del FORMATS
	del _remember

archive, qresult = open_archive(b'simple.7z')

#deinit()