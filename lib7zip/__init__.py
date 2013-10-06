"""
Python bindings to the 7-Zip Library
"""

__author__ = 'Mark Harviston <mark.harviston@gmail.com>'
__license__ = 'BSD'
__version__ = '0.1'

from collections import namedtuple
from functools import partial
import os.path

import logging
from logging import StreamHandler
log = logging.getLogger('lib7zip')
log.addHandler(StreamHandler())

from cffi import FFI
ffi = FFI()

from . import wintypes, py7ziptypes, comtypes
from .py7ziptypes import FormatProps

ffi.cdef(wintypes.CDEFS)
ffi.cdef(comtypes.CDEFS)
ffi.cdef(py7ziptypes.CDEFS)

ffi.cdef("""

HRESULT GetMethodProperty(uint32_t index, PROPID propID, PROPVARIANT * value);
HRESULT GetNumberOfMethods(uint32_t * numMethods);
HRESULT GetNumberOfFormats(uint32_t * numFormats);
HRESULT GetHandlerProperty(PROPID propID, PROPVARIANT * value); /* Unused */
HRESULT GetHandlerProperty2(uint32_t index, PROPID propID, PROPVARIANT * value);
HRESULT CreateObject(const GUID * clsID, const GUID * iid, void ** outObject);
HRESULT SetLargePageMode(); /* Unused */

void* calloc(size_t, size_t);
void free(void*);

""")

dll_path = os.environ.get('7ZDLL_PATH')
if dll_path:
	log.info('DLL path set in environment')
else:
	log.info('autodetecting dll path from registry')
	from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ

	aKey = OpenKey(HKEY_LOCAL_MACHINE, r"SOFTWARE\7-Zip", 0 , KEY_READ)
	s7z_path = QueryValueEx(aKey, "Path")[0]
	dll_path = os.path.join(s7z_path, '7z.dll')

log.info('dll_path: %s', dll_path)
dll7z = ffi.dlopen(dll_path)

C = ffi.dlopen(None)
ole32 = ffi.dlopen('ole32')

from .winhelpers import get_prop_val, guidp2uuid, alloc_propvariant, RNOK

def get_prop(idx, propid, get_fn, prop_name, convert, istype=None):
	tmp_pvar = alloc_propvariant()
	as_pvar = ffi.cast('PROPVARIANT*', tmp_pvar)
	#log.debug('get_prop')

	RNOK(get_fn(idx, propid, as_pvar))

	if as_pvar.vt in (wintypes.VT_EMPTY, wintypes.VT_NULL):
		#log.debug('NULL or empty')
		return None
		
	if istype is not None:
		#log.debug('vt: {:d}'.format(as_pvar.vt))
		assert as_pvar.vt == istype

	return convert(getattr(as_pvar, prop_name))

get_bytes_prop = partial(get_prop, prop_name='pcVal', istype=wintypes.VT_BSTR, convert=ffi.string)
get_string_prop = partial(get_prop, prop_name='bstrVal', istype=wintypes.VT_BSTR, convert=ffi.string)
get_classid = partial(get_prop, prop_name='puuid', istype=wintypes.VT_BSTR, convert=guidp2uuid)
get_hex_prop = partial(get_prop, prop_name='uintVal', istype=wintypes.VT_UI4, convert=lambda x: hex(int(x)))
get_bool_prop = partial(get_prop, prop_name='bVal', istype=wintypes.VT_BOOL, convert=lambda x: x != 0)

Format = namedtuple('Format', ('classid', 'extensions', 'index', 'start_signature'))

def get_format_info():
	num_formats = ffi.new("uint32_t*")
	RNOK(dll7z.GetNumberOfFormats(num_formats))
	assert num_formats != ffi.NULL

	return {
		get_string_prop(i, FormatProps.kName, dll7z.GetHandlerProperty2):
		Format(
			classid=get_classid(i, FormatProps.kClassID, dll7z.GetHandlerProperty2),
			extensions=tuple(get_string_prop(i, FormatProps.kExtension, dll7z.GetHandlerProperty2).split()),
			index=i,
			start_signature=get_bytes_prop(i, FormatProps.kStartSignature, dll7z.GetHandlerProperty2),
		)
		for i in range(num_formats[0])
	}

formats = get_format_info()
max_sig_size = max(len(f.start_signature) for f in formats.values())
#methods = get_method_info()

from .archive import Archive  # noqa