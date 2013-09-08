"""
Helper functions for dealing with windows types defined in wintypes like PROPVARIANT, GUID*, and HRESULT
"""

import uuid
from . import ffi, C, ole32, log
from .wintypes import *

def guidp2uuid(guid):
	"""GUID* -> uuid.UUID"""
	return uuid.UUID(bytes_le=bytes(guid[0]))

def uuid2guidp(uu):
	"""uuid.UUID -> GUID*"""
	return ffi.new('GUID*', uu.bytes_le)

def RNOK(status):
	""" raise error if not S_OK """
	# TODO raise different Exception based on result
	assert int(status) == S_OK

def dealloc_propvariant(pvar):
	ole32.PropVariantClear(pvar)
	C.free(pvar)

def alloc_propvariant():
	return ffi.gc(C.calloc(1, ffi.sizeof('PROPVARIANT')), dealloc_propvariant)
	
def get_prop_val(fn, forcetype=None, checktype=None):
	"""
	fn should have the signature:
	HRESULT fn(PROPVARIANT*);
	"""
	ptr = alloc_propvariant()
	RNOK(fn(ptr))
	pvar = ffi.cast('PROPVARIANT*', ptr)
	vt = forcetype or pvar.vt
	if pvar.vt in (VT_EMPTY, VT_NULL):
		# always check for null, pvar.vt is not a bug
		return None
		
	if checktype:
		if checktype == True:
			checktype = forcetype
		assert pvar.vt == checktype

	if vt in (VT_UI4, VT_UINT):
		return int(pvar.ulVal)
	elif vt == VT_UI8:
		return int(pvar.uhVal)
	elif vt == VT_BOOL:
		return int(pvar.bVal) != 0
	elif vt == VT_CLSID:
		return guidp2uu(pvar.puuid)
	elif vt == VT_BSTR:
		return ffi.string(pvar.bstrVal)
	else:
		raise TypeError("type code %d not supported" % vt)