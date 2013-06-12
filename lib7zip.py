#!/usr/bin/python
# ⓒ  2013 Mark Harviston <mark.harviston@gmail.com>
# BSD License
"""
Python bindings for lib7zip
"""

from itertools import count
import atexit
from cffi import FFI
ffi = FFI()

ffi.cdef(
	"typedef void c7z_Library;"
	"typedef void c7z_InStream;"
	"typedef void c7z_Archive;"
	"typedef void c7z_ArchiveItem;"

	"typedef _Bool bool;\n"

	'#define kpidNoProperty ...\n'
	'#define kpidMainSubfile ...\n'
	'#define kpidHandlerItemIndex ...\n'
	'#define kpidPath ...\n'
	'#define kpidName ...\n'
	'#define kpidExtension ...\n'
	'#define kpidIsDir ...\n'
	'#define kpidSize ...\n'
	'#define kpidPackSize ...\n'
	'#define kpidAttrib ...\n'
	'#define kpidCTime ...\n'
	'#define kpidATime ...\n'
	'#define kpidMTime ...\n'
	'#define kpidSolid ...\n'
	'#define kpidCommented ...\n'
	'#define kpidEncrypted ...\n'
	'#define kpidSplitBefore ...\n'
	'#define kpidSplitAfter ...\n'
	'#define kpidDictionarySize ...\n'
	'#define kpidCRC ...\n'
	'#define kpidType ...\n'
	'#define kpidIsAnti ...\n'
	'#define kpidMethod ...\n'
	'#define kpidHostOS ...\n'
	'#define kpidFileSystem ...\n'
	'#define kpidUser ...\n'
	'#define kpidGroup ...\n'
	'#define kpidBlock ...\n'
	'#define kpidComment ...\n'
	'#define kpidPosition ...\n'
	'#define kpidPrefix ...\n'
	'#define kpidNumSubDirs ...\n'
	'#define kpidNumSubFiles ...\n'
	'#define kpidUnpackVer ...\n'
	'#define kpidVolume ...\n'
	'#define kpidIsVolume ...\n'
	'#define kpidOffset ...\n'
	'#define kpidLinks ...\n'
	'#define kpidNumBlocks ...\n'
	'#define kpidNumVolumes ...\n'
	'#define kpidTimeType ...\n'
	'#define kpidBit64 ...\n'
	'#define kpidBigEndian ...\n'
	'#define kpidCpu ...\n'
	'#define kpidPhySize ...\n'
	'#define kpidHeadersSize ...\n'
	'#define kpidChecksum ...\n'
	'#define kpidCharacts ...\n'
	'#define kpidVa ...\n'
	'#define kpidId ...\n'
	'#define kpidShortName ...\n'
	'#define kpidCreatorApp ...\n'
	'#define kpidSectorSize ...\n'
	'#define kpidPosixAttrib ...\n'
	'#define kpidLink ...\n'
	'#define kpidError ...\n'
	'#define kpidTotalSize ...\n'
	'#define kpidFreeSpace ...\n'
	'#define kpidClusterSize ...\n'
	'#define kpidVolumeName ...\n'
	'#define kpidLocalName ...\n'
	'#define kpidProvider ...\n'
	'#define kpidUserDefined ...\n'

	"""typedef enum {
		NO_ERROR,
		UNKNOWN_ERROR,
		NOT_INITIALIZE,
		NEED_PASSWORD,
		NOT_SUPPORTED_ARCHIVE,
		...
	} ErrorCodeEnum;"""

	"c7z_Library* create_C7ZipLibrary();"
	"void free_C7ZipLibrary(c7z_Library* self);"
	"bool c7zLib_Initialize(c7z_Library* self);"
	"void c7zLib_Deinitialize(c7z_Library* self);"
	"bool c7zLib_OpenArchive(c7z_Library* self, c7z_InStream* pInStream,"
		"c7z_Archive ** ppArchive);"
	"ErrorCodeEnum c7zLib_GetLastError(c7z_Library* self);"

	"c7z_InStream* create_c7zInSt_Filename(const char* filename);"
	"void free_C7ZipInStream(c7z_InStream* stream);"

	"void free_C7ZipArchive(c7z_Archive* self);"

	"bool c7zArc_GetItemCount(c7z_Archive* self, unsigned int * pNumItems);"
	"bool c7zArc_GetItemInfo(c7z_Archive* self, unsigned int index,"
		"c7z_ArchiveItem ** ppArchiveItem);"

	"void c7zArc_Close(c7z_Archive* self);"

	"const wchar_t* c7zItm_GetFullPath(c7z_ArchiveItem* self);"
	"bool c7zItm_IsDir(c7z_ArchiveItem* self);"

	"bool c7zItm_GetUInt64Property(c7z_Archive* self, int propertyIndex,"
		"unsigned long long int * val);"
	"bool c7zItm_GetBoolProperty(c7z_Archive* self, int propertyIndex,"
		"bool* const val);"
	"bool c7zItm_GetStringProperty(c7z_Archive* self, int propertyIndex,"
		"wchar_t ** val);"
	"bool c7zItm_GetFileTimeProperty(c7z_Archive* self, int propertyIndex,"
		"unsigned long long int * val);"

	"bool c7zLib_GetSupportedExts(c7z_Library* self, const wchar_t *** exts,"
		"unsigned int * size);"
	"void free_extarr(const wchar_t** exts);"
)

dll7z = ffi.verify("#include <clib7zip.h>", libraries=['c7zip'])

lib = dll7z.create_C7ZipLibrary()
dll7z.c7zLib_Initialize(lib)


@atexit.register
def deinitialize():
	dll7z.c7zLib_Deinitialize(lib)
	dll7z.free_C7ZipLibrary(lib)


class UnknownError(Exception):
	"""An unknown error has occurred."""


class NotInitialize(Exception):
	"""lib7zip not initialized, it should have been initialized on import"""


class NeedPassword(Exception):
	"""Archive or item in Archive requires a password"""


class NotSupportedArchive(Exception):
	"""The archive type you are trying to open is not supported"""


import sys
if sys.version_info.major < 3:
	range = xrange
else:
	unicode = str
	long = int


def raise_error(msg):
	errcode = dll7z.c7zLib_GetLastError(lib)
	if errcode == dll7z.NOT_INITIALIZE:
		raise NotInitialize(msg)
	elif errcode == dll7z.NEED_PASSWORD:
		raise NeedPassword(msg)
	elif errcode == dll7z.NOT_SUPPORTED_ARCHIVE:
		raise NotSupportedArchive(msg)
	else:
		raise UnknownError(msg)


def get_supported_exts():
	buf = ffi.new("wchar_t ***")
	size = ffi.new("unsigned int *")
	dll7z.c7zLib_GetSupportedExts(lib, buf, size)

	for i in range(0, size[0]):
		def it():
			for j in count():
				r = buf[0][i][j]
				if r == u'\0':
					break
				else:
					yield r

		yield ''.join(it())

	dll7z.free_extarr(buf[0])


class Archive(object):
	def __init__(self, file):
		if isinstance(file, unicode):
			file = file.encode('utf8')

		self.stream = dll7z.create_c7zInSt_Filename(file)
		self.archive = ffi.new("c7z_Archive**")

		if not dll7z.c7zLib_OpenArchive(lib, self.stream, self.archive):
			raise_error("Failed to open %s" % file)

		self.closed = False

	def __del__(self):
		self.close()

	def close(self):
		if not self.closed:
			dll7z.c7zArc_Close(self.archive[0])
			dll7z.free_C7ZipArchive(self.archive[0])
			dll7z.free_C7ZipInStream(self.stream)
			self.closed=True

	def __len__(self):
		count = ffi.new("unsigned int*")
		dll7z.c7zArc_GetItemCount(self.archive[0], count)
		return count[0]

	def __getitem__(self, index):
		item = ffi.new("c7z_ArchiveItem**")
		if not dll7z.c7zArc_GetItemInfo(self.archive[0], index, item):
			raise_error()

		return ArchiveItem(item)

	def __iter__(self):
		for i in range(len(self)):
			yield self[i]


class ArchiveItem(object):
	def __init__(self, item):
		self.item = item

	@property
	def path(self):
		return ffi.string(dll7z.c7zItm_GetFullPath(self.item[0]))

	@property
	def crc(self):
		return self.getUint64Prop(dll7z.kpidCRC)

	@property
	def isdir(self):
		return dll7z.c7zItm_IsDir(self.item[0])

	def getUint64Prop(self, prop):
		if isinstance(prop, unicode):
			prop = getattr(dll7z, 'kpid' + prop)

		val = ffi.new("unsigned long long int*")
		dll7z.c7zItm_GetUInt64Property(self.item[0], prop, val)
		return val[0]

	def getStringProp(self, prop):
		if isinstance(prop, unicode):
			prop = getattr(dll7z, 'kpid' + prop)
		val = ffi.new("unsigned long long int*")
		dll7z.c7zItm_GetStringProperty(self.item[0], prop, val)
		return val[0]
