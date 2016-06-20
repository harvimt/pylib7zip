import lib7zip
import typing

def test_get_7z_version():
	assert lib7zip.get_7z_version() == b'9.20'

def test_get_formats():
	for type_name in lib7zip.get_types():
		print(type_name)
	
#def test_open_real_file_clib():
	#lib7zip.lib.open_archive()