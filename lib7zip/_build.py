import pathlib
import itertools

workdir = pathlib.Path(__file__).resolve().parent
WINDOWS = True  # TODO
if WINDOWS:
	srcdir = workdir.parent / '7z-src'
else:
	srcdir = workdir.parent / 'p7z-src'

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

extern "Python+C" HRESULT py_file_read(void* file, void *data, uint32_t size, uint32_t *processedSize);
extern "Python+C" HRESULT py_file_write(void* file, const void *data, uint32_t size, uint32_t *processedSize);
extern "Python+C" HRESULT py_file_seek(void* file, uint64_t offset, int32_t seekOrigin, uint64_t *newPosition);
extern "Python+C" HRESULT py_file_getsize(void* file, uint64_t* size);
extern "Python+C" HRESULT py_file_setsize(void* file, uint64_t size);
extern "Python+C" HRESULT py_file_close(void* file);
""")

source_files =[
	str(p) for p in itertools.chain(
		[workdir / 'clib7zip.cpp'],
		#(p for p in srcdir.glob('CPP/Common/*.cpp') if p.name not in {'CommandLineParser.cpp', 'C_FileIO.cpp'}),
		#srcdir.glob('CPP/Windows/*.cpp'),
		#(p for p in srcdir.glob('CPP/Common/*.cpp') if p.name not in ('C_FileIO.cpp', 'Random.cpp', 'StdInStream.cpp', 'StdOutStream.cpp')),

		(srcdir / 'CPP/Common' / p for p in (
			'CRC.cpp',
			'IntToString.cpp',
			'ListFileUtils.cpp',
			#'StdInStream.cpp',
			#'StdOutStream.cpp',
			'MyString.cpp',
			'MyWindows.cpp',
			'StringConvert.cpp',
			'StringToInt.cpp',
			'UTFConvert.cpp',
			'MyVector.cpp',
			'Wildcard.cpp',
		)),
		#(srcdir / 'CPP/Windows' / p for p in (
		#	'COM.cpp',
		#	'Error.cpp',
		#	'FileDir.cpp',
		#	'FileFind.cpp',
		#	'FileIO.cpp',
		#	'FileName.cpp',
		#	'PropVariant.cpp',
		#	'PropVariantConversions.cpp',
		#	'Synchronization.cpp',
		#	'System.cpp',
		#	'NationalTime.cpp',
		#)),
		(p for p in srcdir.glob('CPP/Windows/*.cpp') if p.name not in ('Net.cpp', 'Registry.cpp', 'MemoryLock.cpp', 'CommonDialog.cpp', 'Security.cpp', 'Shell.cpp')),
		(srcdir / 'CPP/7zip/Common' / p for p in (
			'CreateCoder.cpp',
			'CWrappers.cpp',
			'FilePathAutoRename.cpp',
			'FileStreams.cpp',
			'FilterCoder.cpp',
			'InBuffer.cpp',
			'InOutTempBuffer.cpp',
			'LimitedStreams.cpp',
			'LockedStream.cpp',
			'MemBlocks.cpp',
			'MethodId.cpp',
			'MethodProps.cpp',
			'OffsetStream.cpp',
			'OutBuffer.cpp',
			'OutMemStream.cpp',
			'ProgressMt.cpp',
			'ProgressUtils.cpp',
			'StreamBinder.cpp',
			'StreamObjects.cpp',
			'StreamUtils.cpp',
			'VirtThread.cpp',
		)),
		#(p for p in srcdir.glob('CPP/7zip/Common/*.cpp') if p.name not in ()),
		#(p for p in srcdir.glob('CPP/7zip/UI/Common/*.cpp') if p.name not in ('CompressCall.cpp', 'CompressCall2.cpp', 'ZipRegistry.cpp')),
		(srcdir / 'CPP/7zip' / p for p in (
			#'Archive/DllExports.cpp',
			'Archive/DllExports2.cpp',
			'Archive/ArchiveExports.cpp',
			'Archive/Bz2Handler.cpp',

			'Archive/DeflateProps.cpp',
			'Archive/GzHandler.cpp',
			'Archive/LzmaHandler.cpp',
			'Archive/PpmdHandler.cpp',
			'Archive/SplitHandler.cpp',
			'Archive/XzHandler.cpp',
			'Archive/ZHandler.cpp',

			'Archive/Common/CoderMixer2.cpp',
			'Archive/Common/CoderMixer2MT.cpp',
			'Archive/Common/CrossThreadProgress.cpp',
			'Archive/Common/DummyOutStream.cpp',
			'Archive/Common/FindSignature.cpp',
			'Archive/Common/HandlerOut.cpp',
			'Archive/Common/InStreamWithCRC.cpp',
			'Archive/Common/ItemNameUtils.cpp',
			'Archive/Common/MultiStream.cpp',
			'Archive/Common/OutStreamWithCRC.cpp',
			'Archive/Common/ParseProperties.cpp',

			'Archive/7z/7zCompressionMode.cpp',
			'Archive/7z/7zDecode.cpp',
			'Archive/7z/7zEncode.cpp',
			'Archive/7z/7zExtract.cpp',
			'Archive/7z/7zFolderInStream.cpp',
			'Archive/7z/7zFolderOutStream.cpp',
			'Archive/7z/7zHandler.cpp',
			'Archive/7z/7zHandlerOut.cpp',
			'Archive/7z/7zHeader.cpp',
			'Archive/7z/7zIn.cpp',
			'Archive/7z/7zOut.cpp',
			'Archive/7z/7zProperties.cpp',
			'Archive/7z/7zSpecStream.cpp',
			'Archive/7z/7zUpdate.cpp',
			'Archive/7z/7zRegister.cpp',

			'Archive/Cab/CabBlockInStream.cpp',
			'Archive/Cab/CabHandler.cpp',
			'Archive/Cab/CabHeader.cpp',
			'Archive/Cab/CabIn.cpp',
			'Archive/Cab/CabRegister.cpp',

			'Archive/Tar/TarHandler.cpp',
			'Archive/Tar/TarHandlerOut.cpp',
			'Archive/Tar/TarHeader.cpp',
			'Archive/Tar/TarIn.cpp',
			'Archive/Tar/TarOut.cpp',
			'Archive/Tar/TarRegister.cpp',
			'Archive/Tar/TarUpdate.cpp',

			'Archive/Zip/ZipAddCommon.cpp',
			'Archive/Zip/ZipHandler.cpp',
			'Archive/Zip/ZipHandlerOut.cpp',
			'Archive/Zip/ZipHeader.cpp',
			'Archive/Zip/ZipIn.cpp',
			'Archive/Zip/ZipItem.cpp',
			'Archive/Zip/ZipOut.cpp',
			'Archive/Zip/ZipUpdate.cpp',
			'Archive/Zip/ZipRegister.cpp',

			'Compress/CodecExports.cpp',
			'Compress/Bcj2Coder.cpp',
			'Compress/Bcj2Register.cpp',
			'Compress/BcjCoder.cpp',
			'Compress/BcjRegister.cpp',
			'Compress/BitlDecoder.cpp',
			'Compress/BranchCoder.cpp',
			'Compress/BranchMisc.cpp',
			'Compress/BranchRegister.cpp',
			'Compress/ByteSwap.cpp',
			'Compress/BZip2Crc.cpp',
			'Compress/BZip2Decoder.cpp',
			'Compress/BZip2Encoder.cpp',
			'Compress/BZip2Register.cpp',
			'Compress/CopyCoder.cpp',
			'Compress/CopyRegister.cpp',
			'Compress/Deflate64Register.cpp',
			'Compress/DeflateDecoder.cpp',
			'Compress/DeflateEncoder.cpp',
			'Compress/DeflateRegister.cpp',
			'Compress/DeltaFilter.cpp',
			'Compress/ImplodeDecoder.cpp',
			'Compress/ImplodeHuffmanDecoder.cpp',
			'Compress/Lzma2Decoder.cpp',
			'Compress/Lzma2Encoder.cpp',
			'Compress/Lzma2Register.cpp',
			'Compress/LzmaDecoder.cpp',
			'Compress/LzmaEncoder.cpp',
			'Compress/LzmaRegister.cpp',
			'Compress/LzOutWindow.cpp',
			'Compress/Lzx86Converter.cpp',
			'Compress/LzxDecoder.cpp',
			'Compress/PpmdDecoder.cpp',
			'Compress/PpmdEncoder.cpp',
			'Compress/PpmdRegister.cpp',
			'Compress/PpmdZip.cpp',
			'Compress/QuantumDecoder.cpp',
			'Compress/ShrinkDecoder.cpp',
			'Compress/ZDecoder.cpp',

			'Crypto/7zAes.cpp',
			'Crypto/7zAesRegister.cpp',
			'Crypto/HmacSha1.cpp',
			'Crypto/MyAes.cpp',
			'Crypto/Pbkdf2HmacSha1.cpp',
			'Crypto/RandGen.cpp',
			'Crypto/Sha1.cpp',
			'Crypto/WzAes.cpp',
			'Crypto/ZipCrypto.cpp',
			'Crypto/ZipStrong.cpp',
		)),
		srcdir.glob('C/*.c'),
		#(srcdir / 'C' / p for p in (
		#	'Aes.c',
		#	'AesOpt.c',
		#	'7zStream.c',
		#	'Alloc.c',
		#	'Bra.c',
		#	'Bra86.c',
		#	'BraIA64.c',
		#	'BwtSort.c',
		#	'Delta.c',
		#	'HuffEnc.c',
		#	'LzFind.c',
		#	'LzFindMt.c',
		#	'Lzma2Dec.c',
		#	'Lzma2Enc.c',
		#	'LzmaDec.c',
		#	'LzmaEnc.c',
		#	'MtCoder.c',
		#	'Ppmd7.c',
		#	'Ppmd7Dec.c',
		#	'Ppmd7Enc.c',
		#	'Ppmd8.c',
		#	'Ppmd8Dec.c',
		#	'Ppmd8Enc.c',
		#	'Sha256.c',
		#	'Sort.c',
		#	'Threads.c',
		#	'Xz.c',
		#	'XzCrc64.c',
		#	'XzDec.c',
		#	'XzEnc.c',
		#	'XzIn.c',
		#	'7zCrc.c',
		#	'7zCrcOpt.c',
		#)),
	)
]

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

extern int g_CodePage = -1;

HRESULT py_file_read(void* file, void *data, uint32_t size, uint32_t *processedSize);
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
		('UNICODE', True),
		('_UNICODE', True),
    ],
	sources=source_files,
	libraries=['user32','OleAut32', 'ole32']
)

if __name__ == '__main__':
	ffi.compile(verbose=True)