import uuid

IID_IUnknown = uuid.UUID('{00000000-0000-0000-C000-000000000046}')

CDEF_IUnknown = """
	HRESULT (*QueryInterface) (void*, GUID*, void**);
	uint32_t (*AddRef)(void*);
	uint32_t (*Release)(void*);
"""

CDEFS = """
typedef struct {
	""" + CDEF_IUnknown + """
} _IUnknown_vtable;

typedef struct {
	_IUnknown_vtable* vtable;
} IUnknown;
"""
