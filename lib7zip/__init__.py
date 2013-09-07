from collections import namedtuple
from functools import partial

import uuid

import logging
from logging import StreamHandler
log = logging.getLogger('lib7zip')
log.setLevel(logging.DEBUG)
log.addHandler(StreamHandler())

from cffi import FFI
ffi = FFI()

from . import wintypes, py7ziptypes, comtypes
from .wintypes import S_OK, guidp2uuid
from .py7ziptypes import FormatProps, MethodProps

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

dll7z = ffi.dlopen('7z.dll')
C = ffi.dlopen(None)
ole32 = ffi.dlopen('ole32')

def alloc(ctype):
	return ffi.gc(C.calloc(1, ffi.sizeof(ctype)), C.free)

def dealloc_propvariant(pvar):
	ole32.PropVariantClear(pvar)
	C.free(pvar)

def alloc_propvariant():
	return ffi.gc(C.calloc(1, ffi.sizeof('PROPVARIANT')), dealloc_propvariant)

def get_prop(idx, propid, get_fn, prop_name, convert, istype=None):
	tmp_pvar = alloc_propvariant()
	as_pvar = ffi.cast('PROPVARIANT*', tmp_pvar)
	#log.debug('get_prop')

	assert get_fn(idx, propid, as_pvar) == wintypes.S_OK

	if istype is not None:
		#log.debug('vt: {:d}'.format(as_pvar.vt))
		assert as_pvar.vt == istype

	if as_pvar.vt in (wintypes.VT_EMPTY, wintypes.VT_NULL):
		log.debug('NULL or empty')
		return None

	return convert(getattr(as_pvar, prop_name))
	#ole32.PropVariantClear(tmp_pvar)
	return r

get_string_prop = partial(get_prop, prop_name='bstrVal', istype=wintypes.VT_BSTR, convert=ffi.string)
get_classid = partial(get_prop, prop_name='puuid', istype=wintypes.VT_BSTR, convert=guidp2uuid)
get_hex_prop = partial(get_prop, prop_name='uintVal', istype=wintypes.VT_UI4, convert=lambda x: hex(int(x)))
get_bool_prop = partial(get_prop, prop_name='bVal', istype=wintypes.VT_BOOL, convert=lambda x: x != 0)

Format = namedtuple('Format', ('classid', 'extensions', 'index'))
class Library():
	def __init__(self):
		self.formats = self._get_format_info()
		self.methods = self._get_method_info()
	
	def destroy(self):
		pass
	
	def __enter__(self, *args, **kwargs):
		pass
	
	def __exit__(self, *args, **kwargs):
		self.destroy()
	
	def __del__(self):
		self.destroy()
	
	def _get_format_info(self):
		num_formats = ffi.new("uint32_t*")
		assert dll7z.GetNumberOfFormats(num_formats) == S_OK
		assert num_formats != ffi.NULL

		return {
			get_string_prop(i, FormatProps.kName, dll7z.GetHandlerProperty2): Format(
				classid=get_classid(i, FormatProps.kClassID, dll7z.GetHandlerProperty2),
				extensions=tuple(get_string_prop(i, FormatProps.kExtension, dll7z.GetHandlerProperty2).split()),
				index=i,
			)
			for i in range(num_formats[0])
		}
	
	def _get_method_info(self):
		#TODO
		pass

@ffi.callback('HRESULT(void* self, uint32_t *numMethods)')
def get_number_of_methods(self, numMethods):
	log.debug('get_number_of_methods')
	return dll7z.GetNumberOfMethods(numMethods)

@ffi.callback('HRESULT(void* self, uint32_t index, PROPID propID, PROPVARIANT *value)')
def get_method_property(self, index, propID, value):
	#log.debug('get_method_property')
	return dll7z.GetMethodProperty(index, propID, value);
	
@ffi.callback('HRESULT(void* self, uint32_t index, const GUID *iid, void **coder)')
def create_decoder(self, index, iid, coder):
	log.debug('create decoder')
	classid = get_prop(
		index,
		py7ziptypes.MethodProps.kDecoder,
		dll7z.GetMethodProperty,
		istype=VT_BSTR)

	#TODO check if decoder assigned
	return dll7z.CreateObject(classid.puuid, iid, coder)
	
@ffi.callback('HRESULT(void* self, uint32_t index, const GUID *iid, void **coder)')
def create_encoder(self, index, iid, coder):
	log.debug('create encoder')
	classid = get_prop(
		index,
		py7ziptypes.MethodProps.kEncoder,
		dll7z.GetMethodProperty,
		istype=VT_BSTR)

	#TODO check if encoder assigned
	return dll7z.CreateObject(classid.puuid, iid, coder)

from .open_callback import ArchiveOpenCallback
from .stream import FileInStream

class Archive:
	def __init__(self, lib, filename):
		format = lib.formats['7z']
		self.tmp_archive = ffi.new('void**')
		
		classid = ffi.new('GUID*', format.classid.bytes_le)
		iid = ffi.new('GUID*', py7ziptypes.IID_IInArchive.bytes_le)
		assert dll7z.CreateObject(classid, iid, self.tmp_archive) == S_OK
		assert self.tmp_archive[0] != ffi.NULL
		self.archive = archive = ffi.cast('IInArchive*', self.tmp_archive[0])
		
		## -- ##
		self.stream = FileInStream(filename)
		stream_inst = self.stream.instances[py7ziptypes.IID_IInStream]
		
		callback = ArchiveOpenCallback(stream=stream_inst)
		callback_inst = callback.instances[py7ziptypes.IID_IArchiveOpenCallback]
		
		maxCheckStartPosition = ffi.new('uint64_t*', 1 << 22)
		#input()
		callback_inst = ffi.NULL
		assert archive.vtable.Open(archive, stream_inst, maxCheckStartPosition, callback_inst) == S_OK
		self.itm_prop_fn = partial(archive.vtable.GetProperty, archive)

	
	def close(self):
		assert self.archive.vtable.Close(self.archive) == S_OK
	
	def __len__(self):
		num_items = ffi.new('uint32_t*')
		assert self.archive.vtable.GetNumberOfItems(self.archive, num_items) == S_OK
		return int(num_items[0])
	
	def __iter__(self):
		for i in range(len(self)):
			isdir = get_bool_prop(i, py7ziptypes.kpidIsDir, self.itm_prop_fn)
			path = get_string_prop(i, py7ziptypes.kpidPath, self.itm_prop_fn)
			crc = get_hex_prop(i, py7ziptypes.kpidCRC, self.itm_prop_fn)
			yield isdir, path, crc
		