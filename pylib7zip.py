from cffi import FFI
P7ZIPSOURCE='p7zip_9.20.1'

ffi = FFI()
ffi.set_unicode(True)

with open("windowsdefs.h") as f:
    ffi.cdef(f.read())

with open(P7ZIPSOURCE + "/CPP/7zip/PropID.h") as f:
    ffi.cdef('\n'.join(l for l in f if not l.startswith('#')))

ffi.cdef("""
const GUID IID_IInArchive;

enum {
    NArchive_kName = 0,
    NArchive_kClassID,
    NArchive_kExtension,
    NArchive_kAddExtension,
    NArchive_kUpdate,
    NArchive_kKeepName,
    NArchive_kStartSignature,
    NArchive_kFinishSignature,
    NArchive_kAssociate
};

uint32_t GetNumberOfFormats(uint32_t*);
uint32_t GetNumberOfMethods(uint32_t *);
uint32_t GetMethodProperty(uint32_t index, uint32_t propID, void * value);
uint32_t GetHandlerProperty2(uint32_t, uint32_t propID, void *);
uint32_t CreateObject(GUID *, GUID *, void **);

PROPVARIANT* create_propvariant();
void destroy_propvariant(PROPVARIANT*);

typedef struct IInArchive IInArchive;
typedef struct IInStream IInStream;

//IInStream
typedef HRESULT (*_stream_read_callback)
    (void* self, void *data, uint32_t size, uint32_t *processedSize);
typedef HRESULT (*_stream_seek_callback)
    (void* self, uint64_t offset, int32_t seekOrigin, uint64_t *newPosition);
typedef HRESULT (*_stream_get_size_callback)(void* self, uint64_t *size);

IInStream* create_instream_from_file(FILE* file);

//IArchiveOpenCallback
typedef HRESULT (*_set_total_callback)
    (void* self, const uint64_t * files, const uint64_t * bytes);
typedef HRESULT (*_set_completed_callback)
    (void* self, const uint64_t * files, const uint64_t * bytes);
typedef HRESULT (*_get_password_callback)(void* self, wchar_t** password);

//IInArchive
void archive_release(IInArchive* archive);
HRESULT archive_open(
    IInArchive* archive,
    IInStream* in_stream,
    void* data /* optional - passed to callbacks as first arg */,
    wchar_t* password, /* optional */
    _get_password_callback get_password_callback, /* optional - takes precedence over password */
    _set_total_callback set_total_callback, /* optional */
    _set_completed_callback set_completed_callback /* optional */);

HRESULT archive_get_num_items(IInArchive* archive, uint32_t* num_items);
HRESULT archive_get_item_property_pvar(
    IInArchive* archive, uint32_t index, uint32_t prop, PROPVARIANT* pvar);

HRESULT archive_close(IInArchive*);
""")

clib7zip = ffi.verify(
    """
    #include "windowsdefs.h"
    #include "clib7zip.h"
    """,
    #modulename='clib7zip',
    sources=[
        'clib7zip.cpp',
        P7ZIPSOURCE + '/CPP/myWindows/wine_date_and_time.cpp',
        P7ZIPSOURCE + '/CPP/myWindows/myGetTickCount.cpp',
        P7ZIPSOURCE + '/CPP/Common/CRC.cpp',
        P7ZIPSOURCE + '/CPP/Common/IntToString.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyMap.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyString.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyWindows.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyXml.cpp',
        P7ZIPSOURCE + '/CPP/Common/StringConvert.cpp',
        P7ZIPSOURCE + '/CPP/Common/StringToInt.cpp',
        P7ZIPSOURCE + '/CPP/Common/UTFConvert.cpp',
        P7ZIPSOURCE + '/CPP/Common/MyVector.cpp',
        P7ZIPSOURCE + '/CPP/Common/Wildcard.cpp',
        P7ZIPSOURCE + '/CPP/Windows/PropVariant.cpp',
        P7ZIPSOURCE + '/CPP/Windows/PropVariantUtils.cpp',
        P7ZIPSOURCE + '/CPP/Windows/Synchronization.cpp',
        P7ZIPSOURCE + '/CPP/Windows/System.cpp',
        P7ZIPSOURCE + '/CPP/Windows/Time.cpp',
        P7ZIPSOURCE + '/CPP/Windows/FileDir.cpp',
        P7ZIPSOURCE + '/CPP/Windows/FileFind.cpp',
        P7ZIPSOURCE + '/CPP/Windows/FileIO.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/InBuffer.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/InOutTempBuffer.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/CreateCoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/CWrappers.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/FilterCoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/LimitedStreams.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/LockedStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/MethodId.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/MethodProps.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/MemBlocks.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/OffsetStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/OutBuffer.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/OutMemStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/ProgressMt.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/ProgressUtils.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/StreamBinder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/StreamObjects.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/StreamUtils.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Common/VirtThread.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/ArchiveExports.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/DllExports2.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/ApmHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/ArjHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Bz2Handler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/CpioHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/CramfsHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/DebHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/DeflateProps.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/DmgHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/ElfHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/FatHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/FlvHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/GzHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/LzhHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/LzmaHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/MachoHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/MbrHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/MslzHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/MubHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/NtfsHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/PeHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/PpmdHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/RpmHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/SplitHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/SquashfsHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/SwfHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/VhdHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/XarHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/XzHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/ZHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/CoderMixer2.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/CoderMixer2MT.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/CrossThreadProgress.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/DummyOutStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/FindSignature.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/InStreamWithCRC.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/ItemNameUtils.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/MultiStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/OutStreamWithCRC.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/OutStreamWithSha1.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/HandlerOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Common/ParseProperties.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zCompressionMode.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zDecode.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zEncode.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zExtract.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zFolderInStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zFolderOutStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zHandlerOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zProperties.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zSpecStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zUpdate.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/7z/7zRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Cab/CabBlockInStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Cab/CabHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Cab/CabHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Cab/CabIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Cab/CabRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Chm/ChmHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Chm/ChmHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Chm/ChmIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Chm/ChmRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Com/ComHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Com/ComIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Com/ComRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Hfs/HfsHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Hfs/HfsIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Hfs/HfsRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Iso/IsoHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Iso/IsoHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Iso/IsoIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Iso/IsoRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Nsis/NsisDecode.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Nsis/NsisHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Nsis/NsisIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Nsis/NsisRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Rar/RarHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Rar/RarHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Rar/RarIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Rar/RarItem.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Rar/RarVolumeInStream.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Rar/RarRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarHandlerOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Tar/TarUpdate.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Udf/UdfHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Udf/UdfIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Udf/UdfRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Wim/WimHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Wim/WimHandlerOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Wim/WimIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Wim/WimRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipAddCommon.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipHandler.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipHandlerOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipHeader.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipIn.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipItem.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipOut.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipUpdate.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Archive/Zip/ZipRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/CodecExports.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ArjDecoder1.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ArjDecoder2.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Bcj2Coder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Bcj2Register.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BcjCoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BcjRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BitlDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BranchCoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BranchMisc.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BranchRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ByteSwap.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BZip2Crc.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BZip2Decoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BZip2Encoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/BZip2Register.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/CopyCoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/CopyRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Deflate64Register.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/DeflateDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/DeflateEncoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/DeflateRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/DeltaFilter.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Lzma2Decoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Lzma2Encoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Lzma2Register.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ImplodeDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ImplodeHuffmanDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/LzhDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/LzmaDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/LzmaEncoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/LzmaRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/LzOutWindow.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/Lzx86Converter.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/LzxDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/PpmdDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/PpmdEncoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/PpmdRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/PpmdZip.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/QuantumDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ShrinkDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ZlibDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ZlibEncoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Compress/ZDecoder.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/7zAes.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/7zAesRegister.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/HmacSha1.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/MyAes.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/Pbkdf2HmacSha1.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/RandGen.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/Sha1.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/WzAes.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/Rar20Crypto.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/RarAes.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/ZipCrypto.cpp',
        P7ZIPSOURCE + '/CPP/7zip/Crypto/ZipStrong.cpp',
        P7ZIPSOURCE + '/C/7zBuf2.c',
        P7ZIPSOURCE + '/C/7zStream.c',
        P7ZIPSOURCE + '/C/Aes.c',
        P7ZIPSOURCE + '/C/Alloc.c',
        P7ZIPSOURCE + '/C/Bra.c',
        P7ZIPSOURCE + '/C/Bra86.c',
        P7ZIPSOURCE + '/C/BraIA64.c',
        P7ZIPSOURCE + '/C/BwtSort.c',
        P7ZIPSOURCE + '/C/Delta.c',
        P7ZIPSOURCE + '/C/HuffEnc.c',
        P7ZIPSOURCE + '/C/LzFind.c',
        P7ZIPSOURCE + '/C/LzFindMt.c',
        P7ZIPSOURCE + '/C/Lzma2Dec.c',
        P7ZIPSOURCE + '/C/Lzma2Enc.c',
        P7ZIPSOURCE + '/C/LzmaDec.c',
        P7ZIPSOURCE + '/C/LzmaEnc.c',
        P7ZIPSOURCE + '/C/MtCoder.c',
        P7ZIPSOURCE + '/C/Ppmd7.c',
        P7ZIPSOURCE + '/C/Ppmd7Dec.c',
        P7ZIPSOURCE + '/C/Ppmd7Enc.c',
        P7ZIPSOURCE + '/C/Ppmd8.c',
        P7ZIPSOURCE + '/C/Ppmd8Dec.c',
        P7ZIPSOURCE + '/C/Ppmd8Enc.c',
        P7ZIPSOURCE + '/C/Sha256.c',
        P7ZIPSOURCE + '/C/Sort.c',
        P7ZIPSOURCE + '/C/Xz.c',
        P7ZIPSOURCE + '/C/XzCrc64.c',
        P7ZIPSOURCE + '/C/XzDec.c',
        P7ZIPSOURCE + '/C/XzEnc.c',
        P7ZIPSOURCE + '/C/XzIn.c',
        P7ZIPSOURCE + '/C/7zCrc.c',
        P7ZIPSOURCE + '/C/7zCrcOpt.c',
        P7ZIPSOURCE + '/C/Threads.c',
    ],
    include_dirs=[
        '.', P7ZIPSOURCE + '/CPP',
        P7ZIPSOURCE + '/CPP/7zip/UI/Client7z',
        P7ZIPSOURCE + '/CPP/myWindows',
        P7ZIPSOURCE + '/CPP/include_windows',
    ],
    define_macros=[
        ('_FILE_OFFSET_BITS', '64'),
        ('_LARGEFILE_SOURCE',),
        ('_REENTRENT',),
    ],
)

def RNOK(hresult):
    if hresult != clib7zip.S_OK:
        raise Exception("HRESULT ERROR=%x" % hresult)

def main():
    lib7zip = clib7zip
    ffi2 = ffi
    pvar = ffi.gc(clib7zip.create_propvariant(), clib7zip.destroy_propvariant)
    with open("abc.7z", "rb") as f:
        print("Creating stream...")
        stream = clib7zip.create_instream_from_file(f);
        assert stream != ffi.NULL
        print("...Created")
        print("Creating archive...")
        num_items = ffi.new("uint32_t*")
        RNOK(lib7zip.GetNumberOfFormats(num_items))
        print("num_items=%d" % num_items[0])
        for i in range(num_items[0]):
            print("i=%d" % i)
            RNOK(lib7zip.GetHandlerProperty2(i, clib7zip.NArchive_kName, pvar))
            print("7z=%s" % ffi.string(pvar.bstrVal))
            if ffi.string(pvar.bstrVal) == "7z":
                print("found it")
                break

        print("Creating Archive Object...")
        RNOK(lib7zip.GetHandlerProperty2(i, clib7zip.NArchive_kClassID, pvar))
        archive_p = ffi.new("void**")

        RNOK(lib7zip.CreateObject(
            ffi2.cast("GUID*", pvar.puuid),
            ffi2.cast("GUID*", ffi2.addressof(clib7zip.IID_IInArchive)),
            archive_p,
        ))
        archive = ffi.cast("IInArchive*", archive_p[0])
        assert archive != ffi.NULL
        print("...Created")
        print("Opening...");
        clib7zip.archive_open(archive, stream, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL);
        print("...Opened");
        RNOK(clib7zip.archive_get_num_items(archive, num_items))
        print("num_items=%d" % num_items[0])
        for i in range(num_items[0]):
            print("i=%d" % i)
            RNOK(clib7zip.archive_get_item_property_pvar(archive, i, clib7zip.kpidPath, pvar))
            assert pvar.vt == clib7zip.VT_BSTR
            print("path=%s" % ffi.string(pvar.bstrVal))
        print("Closing...")
        RNOK(clib7zip.archive_close(archive))
        print("...Closing")

if __name__ == '__main__':
    main()
