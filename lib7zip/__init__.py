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

	if as_pvar.vt in (wintypes.VT_EMPTY, wintypes.VT_NULL):
		#log.debug('NULL or empty')
		return None
		
	if istype is not None:
		#log.debug('vt: {:d}'.format(as_pvar.vt))
		assert as_pvar.vt == istype

	return convert(getattr(as_pvar, prop_name))
	#ole32.PropVariantClear(tmp_pvar)
	return r

get_bytes_prop = partial(get_prop, prop_name='pcVal', istype=wintypes.VT_BSTR, convert=ffi.string)
get_string_prop = partial(get_prop, prop_name='bstrVal', istype=wintypes.VT_BSTR, convert=ffi.string)
get_classid = partial(get_prop, prop_name='puuid', istype=wintypes.VT_BSTR, convert=guidp2uuid)
get_hex_prop = partial(get_prop, prop_name='uintVal', istype=wintypes.VT_UI4, convert=lambda x: hex(int(x)))
get_bool_prop = partial(get_prop, prop_name='bVal', istype=wintypes.VT_BOOL, convert=lambda x: x != 0)

Format = namedtuple('Format', ('classid', 'extensions', 'index', 'start_signature'))

def get_format_info():
	num_formats = ffi.new("uint32_t*")
	assert dll7z.GetNumberOfFormats(num_formats) == S_OK
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

from .extract_callback import ArchiveExtractCallback
from .open_callback import ArchiveOpenCallback
from .stream import FileInStream

def RNOK(status):
	""" raise error if not S_OK """
	assert int(status) == S_OK

def uu2guidp(uu):
	return ffi.new('GUID*', uu.bytes_le)

class Archive:
	def __init__(self, filename, forcetype=None, password=None):
		self.tmp_archive = ffi.new('void**')
		iid = uu2guidp(py7ziptypes.IID_IInArchive)

		self.stream = FileInStream(filename)
		stream_inst = self.stream.instances[py7ziptypes.IID_IInStream]
		
		if forcetype is not None:
			format = formats[forcetype]
		else:
			format = self._guess_format()
			
		classid = uu2guidp(format.classid)
		
		RNOK(dll7z.CreateObject(classid, iid, self.tmp_archive))
		assert self.tmp_archive[0] != ffi.NULL
		self.archive = archive = ffi.cast('IInArchive*', self.tmp_archive[0])
		
		callback = ArchiveOpenCallback(password=password)
		callback_inst = callback.instances[py7ziptypes.IID_IArchiveOpenCallback]
		
		maxCheckStartPosition = ffi.new('uint64_t*', 1 << 22)
		RNOK(archive.vtable.Open(archive, stream_inst, maxCheckStartPosition, callback_inst))
		self.itm_prop_fn = partial(archive.vtable.GetProperty, archive)
	
	def _guess_format(self):
		file = self.stream.filelike
		sigcmp = file.read(max_sig_size)
		for name, format in formats.items():
			if format.start_signature and sigcmp.startswith(format.start_signature):
				log.debug('guessed: %s' % name)
				file.seek(0)
				return format

		assert False

	def __enter__(self, *args, **kwargs):
		return self
	
	def __exit__(self, *args, **kwargs):
		self.close()
	
	def __del__(self):
		self.close()
	
	def close(self):
		RNOK(self.archive.vtable.Close(self.archive))
	
	def __len__(self):
		num_items = ffi.new('uint32_t*')
		RNOK(self.archive.vtable.GetNumberOfItems(self.archive, num_items))
		return int(num_items[0])
	
	def __iter__(self):
		for i in range(len(self)):
			isdir = get_bool_prop(i, py7ziptypes.kpidIsDir, self.itm_prop_fn)
			path = get_string_prop(i, py7ziptypes.kpidPath, self.itm_prop_fn)
			crc = get_hex_prop(i, py7ziptypes.kpidCRC, self.itm_prop_fn)
			yield isdir, path, crc
	
	def extract(self):
		'''
IInArchive::Extract:
indices must be sorted
numItems = 0xFFFFFFFF means "all files"
testMode != 0 means "test files without writing to outStream"
		'''
		callback = ArchiveExtractCallback()
		callback_inst = callback.instances[py7ziptypes.IID_IArchiveExtractCallback]
		indices = ffi.new('uint32_t[]', [])
		RNOK(self.archive.vtable.Extract(self.archive, ffi.NULL, 0xFFFFFFFF, 0, callback_inst))
		callback.out_file.filelike.flush()
		callback.out_file.filelike.close()