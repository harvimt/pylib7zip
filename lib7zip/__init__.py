from _lib7zip import ffi, lib

def get_7z_version():
	return ffi.string(lib.C_MY_VERSION)
	
