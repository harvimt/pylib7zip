import atexit
from cffi import FFI
ffi = FFI()

ffi.cdef(
	"typedef void c7z_Library;"
	"typedef void c7z_InStream;"
	"typedef void c7z_Archive;"
	"typedef void c7z_ArchiveItem;"

	"typedef _Bool bool;\n"
	
	"#define kpidCRC ...\n"

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
	"bool c7zLib_OpenArchive(c7z_Library* self, c7z_InStream* pInStream, c7z_Archive ** ppArchive);"
	"ErrorCodeEnum c7zLib_GetLastError(c7z_Library* self);"

	"c7z_InStream* create_c7zInSt_Filename(const char* filename);"
	"void free_C7ZipInStream(c7z_InStream* stream);"

	"void free_C7ZipArchive(c7z_Archive* self);"

	"bool c7zArc_GetItemCount(c7z_Archive* self, unsigned int * pNumItems);"
	"bool c7zArc_GetItemInfo(c7z_Archive* self, unsigned int index, c7z_ArchiveItem ** ppArchiveItem);"

	"void c7zArc_Close(c7z_Archive* self);"

	"const wchar_t* c7zItm_GetFullPath(c7z_ArchiveItem* self);"
	"bool c7zItm_IsDir(c7z_ArchiveItem* self);"

	"bool c7zItm_GetUInt64Property(c7z_Archive* self, int propertyIndex, unsigned long long int * val);"
	"bool c7zItm_GetBoolProperty(c7z_Archive* self, int propertyIndex, bool * const val);"
	"bool c7zItm_GetStringProperty(c7z_Archive* self, int propertyIndex, wchar_t ** val);"
	"bool c7zItm_GetFileTimeProperty(c7z_Archive* self, int propertyIndex, unsigned long long int * val);"
);

dll7z = ffi.verify("#include<clib7zip.h>", libraries=['c7zip'])

lib = dll7z.create_C7ZipLibrary();
dll7z.c7zLib_Initialize(lib);

@atexit.register
def deinitialize():
	dll7z.c7zLib_Deinitialize(lib)
	dll7z.free_C7ZipLibrary(lib)

class UnknownError(Exception): pass
class NotInitialize(Exception): pass
class NeedPassword(Exception): pass
class NotSupportedArchive(Exception): pass

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

def openarchive(filename):
	if isinstance(filename, unicode):
		filename = filename.encode('utf-8')

	instream = dll7z.create_c7zInSt_Filename(filename)
	archive = ffi.new("c7z_Archive**")

	if not dll7z.c7zLib_OpenArchive(lib, instream, archive):
		raise Exception("Failed to open %s" % filename)

	return Archive(lib, archive, instream)

class Archive(object):
	def __init__(self, lib, archive, stream):
		self.lib = lib
		self.archive = archive
		self.stream = stream

	def __del__(self):
		dll7z.c7zArc_Close(self.archive[0])
		dll7z.free_C7ZipArchive(self.archive[0])
		dll7z.free_C7ZipInStream(self.stream[0])
	
	def __len__(self):
		count = ffi.new("unsigned int*")
		dll7z.c7zArc_GetItemCount(self.archive[0], count)
		return count[0]

	def __getitem__(self, index):
		item = ffi.new("c7z_ArchiveItem**")
		if not dll7z.c7zArc_GetItemInfo(self.archive[0], index, item):
			raise_error()

		return ArchiveItem(self.lib, self.archive, item)

	def __iter__(self):
		for i in range(len(self)):
			yield self[i]

class ArchiveItem(object):
	def __init__(self, lib, archive, item):
		self.lib = lib
		self.archive = archive
		self.item = item

	@property
	def path(self):
		return ffi.string(dll7z.c7zItm_GetFullPath(self.item[0]))

	@property
	def crc(self):
		val = ffi.new("unsigned long long int*")
		dll7z.c7zItm_GetUInt64Property(self.item[0], dll7z.kpidCRC, val)
		return val[0]

	@property
	def isdir(self):
		return dll7z.c7zItm_IsDir(self.item[0])
