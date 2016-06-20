from _lib7zip import ffi, lib
from enum import IntEnum

__all__ = ('get_7z_version', 'get_types')

def get_7z_version():
	return ffi.string(lib.C_MY_VERSION)

class HresultException(Exception):
	def __init__(self, hresult, message='no message'):
		super().__init__('0x{:016x} - {}'.format(hresult, message))
	
def RNOK(hresult, message='RNOK failed'):
	if hresult != lib.S_OK:
		raise HresultException(hresult, message)
		
def create_pvar():
	return ffi.gc(lib.create_propvariant(), lib.destroy_propvariant)

def pvar_getval(pvar):
	if pvar.vt == lib.VT_BOOL:
		return bool(pvar.bVal)
	elif pvar.vt == lib.VT_UI4:
		return pvar.ulVal;
	elif pvar.vt == lib.VT_UI8:
		return pvar.uhVal;
	elif pvar.vt == lib.VT_EMPTY or pvar.vt == lib.VT_NULL:
		return None
	elif pvar.vt == lib.VT_ERROR:
		raise Exception("Propvariant Exception")
	elif pvar.vt == lib.VT_BSTR:
		return ffi.string(pvar.bstrVal)
	elif pvar.vt == lib.VT_CLSID:
		return None # TODO handle guid
	elif pvar.vt == lib.VT_FILETIME:
		return None #TODO handle filetime
	else:
		raise Exception("Unhandled Propvariant Type")


def get_types():
	num_formats = ffi.new('uint32_t*')
	RNOK(lib._GetNumberOfFormats(num_formats))
	pvar = create_pvar()
	for i in range(num_formats[0]):
		lib._GetHandlerProperty2(i, lib.NArchive_kName, pvar);
		print(pvar_getval(pvar))

	
@ffi.def_extern
def py_file_read(file, data, size, processedSize):
	try:
		if processedSize != ffi.NULL:
			processedSize[0] = file.readinto(ffi.buffer(data, size))
		else:
			file.readinto(ffi.buffer(data, size))
	except:
		return lib.E_ERROR
	return lib.S_OK
	
@ffi.def_extern
def py_file_read(file, data, size, processedSize):
	try:
		if processedSize != ffi.NULL:
			processedSize[0] = file.write(ffi.buffer(data, size))
		else:
			file.write(ffi.buffer(data, size))
	except:
		return lib.E_ERROR
	return lib.S_OK
	
@ffi.def_extern
def py_file_seek(file, offset, seekOrigin, newPosition):
	try:
		file.seek(offset, seekOrigin)
		if newPosition != ffi.NULL:
			newPosition[0] = file.tell()
	except:
		return lib.E_ERROR
	return lib.S_OK
	
@ffi.def_extern
def py_file_getsize(file, size):
	try:
		if size == ffi.NULL:
			return lib.E_ABORT
		oldloc = file.tell()
		file.seek(0, 2)
		size[0] = file.tell()
		file.seek(oldloc)
	except:
		return lib.E_ERROR
	return lib.S_OK
	
@ffi.def_extern
def py_file_setsize(file, size):
	try:
		file.truncate(size)
	except:
		return lib.E_ERROR
	return lib.S_OK
	
@ffi.def_extern
def py_file_close(file):
	try:
		file.close()
	except:
		return lib.E_ERROR
	return lib.S_OK