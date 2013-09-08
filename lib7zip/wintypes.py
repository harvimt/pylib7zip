"""
"""
CDEFS = """
typedef unsigned short VARTYPE;

typedef uint8_t GUID[16];

typedef struct PROPVARIANT {
	VARTYPE           vt;
	unsigned short    wReserved1;
	unsigned short    wReserved2;
	unsigned short    wReserved3;
	union {
		char              cVal;
		uint8_t           bVal;
		int16_t           iVal;
		uint16_t          uiVal;
		int32_t           lVal;
		uint32_t          ulVal;
		float             fltVal;
		double            dblVal;
		char*             pcVal;
		wchar_t*          bstrVal;
		uint64_t          uhVal;
		GUID*             puuid;
		/* snip */
	};
	} PROPVARIANT;


typedef unsigned long long HRESULT;

HRESULT PropVariantClear(PROPVARIANT *pvar);
"""

#HRESULT values
S_OK = 0x00000000  # Operation successful
E_ABORT = 0x80004004  # Operation aborted
E_ACCESSDENIED = 0x80070005  # General access denied error
E_FAIL = 0x80004005  # 	Unspecified failure
E_HANDLE = 0x80070006  # Handle that is not valid
E_INVALIDARG = 0x80070057  # One or more arguments are not valid
E_NOINTERFACE = 0x80004002  # No such interface supported
E_NOTIMPL = 0x80004001  # Not implemented
E_OUTOFMEMORY = 0x8007000E  # Failed to allocate necessary memory
E_POINTER = 0x80004003  # Pointer that is not valid
E_UNEXPECTED = 0x8000FFFF  # Unexpected failure

#VARTYPE type values
VT_EMPTY = 0
VT_NULL = 1
VT_I1 = 16
VT_UI1 = 17
VT_I2 = 2
VT_UI2 = 18
VT_I4 = 3
VT_UI4 = 19
VT_INT = 22
VT_UINT = 23
VT_I8 = 20
VT_UI8 = 21
VT_R4 = 4
VT_R8 = 5
VT_BOOL = 11
VT_ERROR = 10
VT_CY = 6
VT_DATE = 7
VT_FILETIME = 64
VT_CLSID = 72
VT_CF = 71
VT_BSTR = 8
VT_BSTR_BLOB = 0xfff
VT_BLOB = 65
VT_BLOBOBJECT = 70
VT_LPSTR = 30
VT_LPWSTR = 31
VT_UNKNOWN = 13
VT_DISPATCH = 9
VT_STREAM = 66
VT_STREAMED_OBJECT = 68
VT_STORAGE = 67
VT_STORED_OBJECT = 69
VT_VERSIONED_STREAM = 73
VT_DECIMAL = 14
VT_VECTOR = 0x1000
VT_ARRAY = 0x2000
VT_BYREF = 0x4000
VT_VARIANT = 12
VT_TYPEMASK = 0xFFF