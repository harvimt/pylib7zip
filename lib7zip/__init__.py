from _lib7zip import ffi, lib

def get_7z_version():
	return ffi.string(lib.C_MY_VERSION)
	
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