import pathlib
import itertools

workdir = pathlib.Path(__file__).parent
WINDOWS = True  # TODO
if WINDOWS:
	srcdir = workdir / '7z-src'
else:
	srcdir = workdir / 'p7z-src'

import cffi

ffi = cffi.FFI()


with (workdir / 'clib7zip.cpp').open('r') as f:
	clib7zip_cpp = f.read()
with (workdir / 'clib7zip.h').open('r') as f:
	clib7zip_h_lines = []
	in_body = False
	for line in f:
		if line == '//CDEF START':
			in_body = True
		elif line == '//CDEF END':
			in_body = True
		elif in_body:
			clib7zip_h_lines.append(line)

clib7zip_h = '\n'.join(clib7zip_h_lines)

with (workdir / 'windowsdefs.h').open('r') as f:
	windefs = f.read()
with (workdir / 'propid.h').open('r') as f:
	propid_h = f.read()
	
ffi.cdef(windefs)
ffi.cdef(propid_h)
ffi.cdef(clib7zip_h)
ffi.cdef("""
const char* C_MY_VERSION;
const char* C_MY_7ZIP_VERSION;
const char* C_MY_DATE;
const char* C_MY_COPYRIGHT;
const char* C_MY_VERSION_COPYRIGHT_DATE;
""")

ffi.set_source(
	'_lib7zip',
"""
#include "windowsdefs.h"
#include "7zip/MyVersion.h"
#include "clib7zip.h"

const char* C_MY_VERSION = MY_VERSION;
const char* C_MY_7ZIP_VERSION = MY_7ZIP_VERSION;
const char* C_MY_DATE = MY_DATE;
const char* C_MY_COPYRIGHT = MY_COPYRIGHT;
const char* C_MY_VERSION_COPYRIGHT_DATE = MY_VERSION_COPYRIGHT_DATE;

""",
	include_dirs=[
        workdir,
        str(srcdir / 'CPP'),
        str(srcdir / 'CPP/7zip/UI/Client7z'),
        str(srcdir / 'CPP/myWindows'),
        str(srcdir / 'CPP/include_windows'),
    ],
    define_macros=[
        ('_FILE_OFFSET_BITS', '64'),
        ('_REENTRENT', True),
    ],
	sources=[
		str(p) for p in itertools.chain(
			['clib7zip.cpp'],
			workdir.glob('CPP/Common/*.cpp'),
			workdir.glob('CPP/Windows/*.cpp'),
			workdir.glob('CPP/7zip/Common/*.cpp'),
			workdir.glob('CPP/7zip/Archive/*/*.cpp'),
			workdir.glob('CPP/7zip/Archive/*/*.cpp'),
			workdir.glob('CPP/7zip/Compress/*.cpp'),
			workdir.glob('CPP/7zip/Crypto/*.cpp'),
			workdir.glob('C/*.c'),
		)
	],
)

if __name__ == '__main__':
	ffi.compile()