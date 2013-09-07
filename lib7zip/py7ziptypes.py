import uuid
from .comtypes import CDEF_IUnknown
from string import Template

CDEFS = Template('''
typedef uint32_t PROPID; /*actually an enum, often a different enum for each function...*/

typedef struct {
	$CDEF_IUnknown
	/* Inherited from ISequentialInstream */
	HRESULT (*Read)(void* self, uint8_t *data, uint32_t size, uint32_t *processedSize);
	/* Own methods */
	HRESULT (*Seek)(void* self, int64_t offset, uint32_t seekOrigin, uint64_t *newPosition);
} _IInStream_vtable;

typedef struct{
	_IInStream_vtable* vtable;
} IInStream;

typedef struct {
	$CDEF_IUnknown
	HRESULT (*Write)(void* self, const void *data, uint32_t size, uint32_t *processedSize);
	/*
	if (size > 0) this function must write at least 1 byte.
	This function is allowed to write less than "size".
	You must call Write function in loop, if you need to write exact amount of data
	*/
	HRESULT (*Seek)(void* self, int64_t offset, uint32_t seekOrigin, uint64_t *newPosition);
} _IOutStream_vtable;

typedef struct {
	_IOutStream_vtable* vtable;
} IOutStream;

typedef IOutStream ISequentialOutStream;
typedef IInStream ISequentialInStream;


typedef struct {
	$CDEF_IUnknown
	HRESULT(*SetTotal)(void* self, const uint64_t *files, const uint64_t *bytes);
	HRESULT(*SetCompleted)(void* self, const uint64_t *files, const uint64_t *bytes);
} _IArchiveOpenCallback_vtable;

typedef struct {
	_IArchiveOpenCallback_vtable* vtable;
} IArchiveOpenCallback;

typedef struct {
	$CDEF_IUnknown
	HRESULT(*SetTotal)(void* self, uint64_t total);
	HRESULT(*SetCompleted)(void* self, const uint64_t *completeValue);
	HRESULT(*GetStream)(void* self, uint32_t index, ISequentialOutStream **outStream,  int32_t askExtractMode);
	HRESULT(*PrepareOperation)(void* self, int32_t askExtractMode);
	HRESULT(*SetOperationResult)(void* self, int32_t resultEOperationResult);
} _IArchiveExtractCallback_vtable;

typedef struct {_IArchiveExtractCallback_vtable* vtable; } IArchiveExtractCallback;

typedef struct {
	$CDEF_IUnknown
	HRESULT(*SetRatioInfo)(void* self, const uint64_t *inSize, const uint64_t *outSize);
} _ICompressProgressInfo_vtable;
typedef struct {_ICompressProgressInfo_vtable* vtable;} ICompressProgressInfo;

typedef struct {
	$CDEF_IUnknown
	HRESULT (*Open)(void* self, IInStream *stream, const uint64_t *maxCheckStartPosition, IArchiveOpenCallback *openArchiveCallback);
	HRESULT (*Close)(void* self);
	HRESULT (*GetNumberOfItems)(void* self, uint32_t *numItems);
	HRESULT (*GetProperty)(void* self, uint32_t index, PROPID propID, PROPVARIANT *value);
	HRESULT (*Extract)(void* self, const uint32_t* indices, uint32_t numItems, uint32_t testMode, IArchiveExtractCallback *extractCallback);
	HRESULT (*GetArchiveProperty)(void* self, PROPID propID, PROPVARIANT *value);
	HRESULT (*GetNumberOfProperties)(void* self, uint32_t *numProperties);
	HRESULT (*GetPropertyInfo)(void* self, uint32_t index, wchar_t **name, PROPID *propID, VARTYPE *varType);
	HRESULT (*GetNumberOfArchiveProperties)(void* self, uint32_t *numProperties);
	HRESULT (*GetArchivePropertyInfo)(void* self, uint32_t index, wchar_t **name, PROPID *propID, VARTYPE *varType);
} _IInArchive_vtable;

typedef struct {
	_IInArchive_vtable* vtable;
} IInArchive;

typedef struct {
	$CDEF_IUnknown
	HRESULT(*GetNumberOfMethods)(void* self, uint32_t *numMethods);
	HRESULT(*GetProperty)(void* self, uint32_t index, PROPID propID, PROPVARIANT *value);
	HRESULT(*CreateDecoder)(void* self, uint32_t index, const GUID *iid, void **coder);
	HRESULT(*CreateEncoder)(void* self, uint32_t index, const GUID *iid, void **coder);
 } _ICompressCodecsInfo_vtable;
 
 typedef struct {
 	_ICompressCodecsInfo_vtable* vtable;
 } ICompressCodecsInfo;
  
typedef struct {
	$CDEF_IUnknown
	HRESULT (*SetCompressCodecsInfo)(void* self, ICompressCodecsInfo *compressCodecsInfo);
}_ISetCompressCodecsInfo_vtable;

typedef struct {
	_ISetCompressCodecsInfo_vtable* vtable;
} ISetCompressCodecsInfo;

typedef struct {
    $CDEF_IUnknown
	HRESULT (*CryptoGetTextPassword)(void* self, wchar_t **password);
} _ICryptoGetTextPassword_vtable;
typedef struct { _ICryptoGetTextPassword_vtable* vtable;} ICryptoGetTextPassword;
 
typedef struct {
  $CDEF_IUnknown
  HRESULT (*GetProperty)(void* self, PROPID propID, PROPVARIANT *value);
  HRESULT (*GetStream)(void* self, const wchar_t *name, IInStream **inStream);
} _IArchiveOpenVolumeCallback_vtable;
typedef struct { _IArchiveOpenVolumeCallback_vtable* vtable; } IArchiveOpenVolumeCallback;

typedef struct {
	$CDEF_IUnknown
	HRESULT (*SetSubArchiveName)(void* self, const wchar_t *name);
} _IArchiveOpenSetSubArchiveName_vtable;
typedef struct { _IArchiveOpenSetSubArchiveName_vtable* vtable; } IArchiveOpenSetSubArchiveName;
'''
).substitute(CDEF_IUnknown=CDEF_IUnknown)

class FormatProps:
	kName = 0
	kClassID = 1
	kExtension = 2
	kAddExtension = 3
	kUpdate = 4
	kKeepName = 5
	kStartSignature = 6
	kFinishSignature = 7
	kAssociate = 8

class MethodProps:
	kID = 0
	kName = 1
	kDecoder = 2
	kEncoder = 3 
	kInStreams = 4
	kOutStreams = 5
	kDescription = 6
	kDecoderIsAssigned = 7
	kEncoderIsAssigned = 8


def createIID(yy, xx):
	return uuid.UUID('{{23170F69-40C1-278A-0000-00{yy:s}00{xx:s}0000}}'.format(xx=xx, yy=yy))
#00 IProgress.h

IID_IProgress = createIID('00', '05')

#01 IFolderArchive.h

IID_IArchiveFolder = createIID('01', '05')
IID_IFolderArchiveExtractCallback = createIID('01', '07')
IID_IOutFolderArchive = createIID('01', '0A')
IID_IFolderArchiveUpdateCallback = createIID('01', '0B')
IID_IArchiveFolderInternal = createIID('01', '0C')
IID_IInFolderArchive = createIID('01', '0E')

#03 IStream.h

IID_ISequentialInStream = createIID('03', '01')
IID_ISequentialOutStream = createIID('03', '02')
IID_IInStream = createIID('03', '03')
IID_IOutStream = createIID('03', '04')
IID_IStreamGetSize = createIID('03', '06')
IID_IOutStreamFlush = createIID('03', '07')


#04 ICoder.h

IID_ICompressProgressInfo = createIID('04', '04')
IID_ICompressCoder = createIID('04', '05')
IID_ICompressCoder2 = createIID('04', '18')
IID_ICompressSetCoderProperties = createIID('04', '20')
IID_ICompressSetDecoderProperties2 = createIID('04', '22')
IID_ICompressWriteCoderProperties = createIID('04', '23')
IID_ICompressGetInStreamProcessedSize = createIID('04', '24')
IID_ICompressSetCoderMt = createIID('04', '25')
IID_ICompressGetSubStreamSize = createIID('04', '30')
IID_ICompressSetInStream = createIID('04', '31')
IID_ICompressSetOutStream = createIID('04', '32')
IID_ICompressSetInStreamSize = createIID('04', '33')
IID_ICompressSetOutStreamSize = createIID('04', '34')
IID_ICompressSetBufSize = createIID('04', '35')
IID_ICompressFilter = createIID('04', '40')
IID_ICompressCodecsInfo = createIID('04', '60')
IID_ISetCompressCodecsInfo = createIID('04', '61')
IID_ICryptoProperties = createIID('04', '80')
IID_ICryptoResetSalt = createIID('04', '88')
IID_ICryptoResetInitVector = createIID('04', '8C')
IID_ICryptoSetPassword = createIID('04', '90')
IID_ICryptoSetCRC = createIID('04', 'A0')


#05 IPassword.h

IID_ICryptoGetTextPassword = createIID('05', '10')
IID_ICryptoGetTextPassword2 = createIID('05', '11')


#06 IArchive.h

IID_ISetProperties = createIID('06', '03')
IID_IArchiveOpenCallback = createIID('06', '10')
IID_IArchiveExtractCallback = createIID('06', '20')
IID_IArchiveOpenVolumeCallback = createIID('06', '30')
IID_IInArchiveGetStream = createIID('06', '40')
IID_IArchiveOpenSetSubArchiveName = createIID('06', '50')
IID_IInArchive = createIID('06', '60')
IID_IArchiveOpenSeq = createIID('06', '61')

IID_IArchiveUpdateCallback = createIID('06', '80')
IID_IArchiveUpdateCallback2 = createIID('06', '82')
IID_IOutArchive = createIID('06', 'A0')


#08 IFolder.h
IID_IFolderFolder = createIID('08', '00')
IID_IEnumProperties = createIID('08', '01')
IID_IFolderGetTypeID = createIID('08', '02')
IID_IFolderGetPath = createIID('08', '03')
IID_IFolderWasChanged = createIID('08', '04')
IID_IFolderOperations = createIID('08', '06')
IID_IFolderGetSystemIconIndex = createIID('08', '07')
IID_IFolderGetItemFullSize = createIID('08', '08')
IID_IFolderClone = createIID('08', '09')
IID_IFolderSetFlatMode = createIID('08', '0A')
IID_IFolderOperationsExtractCallback = createIID('08', '0B')
IID_IFolderProperties = createIID('08', '0E')
IID_IFolderArcProps = createIID('08', '10')
IID_IGetFolderArcProps = createIID('08', '11')

#09 IFolder.h :: FOLDER_MANAGER_INTERFACE
#IID_IFolderManager = createIID('09', '00')


#0A PluginInterface.h
#IID_IInitContextMenu = createIID('0A', '0')
#IID_IPluginOptionsCallback = createIID('0A', '00')
#IID_IPluginOptions = createIID('0A', '0')

#PropID.h

kpidNoProperty = 0
kpidMainSubfile = 1
kpidHandlerItemIndex = 2
kpidPath = 3
kpidName = 4
kpidExtension = 5
kpidIsDir = 6
kpidSize = 7
kpidPackSize = 8
kpidAttrib = 9
kpidCTime = 10
kpidATime = 11
kpidMTime = 12
kpidSolid = 13
kpidCommented = 14
kpidEncrypted = 15
kpidSplitBefore = 16
kpidSplitAfter = 17
kpidDictionarySize = 18
kpidCRC = 19
kpidType = 20
kpidIsAnti = 21
kpidMethod = 22
kpidHostOS = 23
kpidFileSystem = 24
kpidUser = 25
kpidGroup = 26
kpidBlock = 27
kpidComment = 27
kpidPosition = 28
kpidPrefix = 29
kpidNumSubDirs = 30
kpidNumSubFiles = 31
kpidUnpackVer = 32
kpidVolume = 33
kpidIsVolume = 34
kpidOffset = 35
kpidLinks = 36
kpidNumBlocks = 37
kpidNumVolumes = 38
kpidTimeType = 39
kpidBit64 = 40
kpidBigEndian = 41
kpidCpu = 42
kpidPhySize = 43
kpidHeadersSize = 44
kpidChecksum = 45
kpidCharacts = 46
kpidVa = 47
kpidId = 48 
kpidShortName = 49
kpidCreatorApp = 50
kpidSectorSize = 51
kpidPosixAttrib = 52
kpidLink = 53
kpidError = 54

kpidTotalSize = 0x1100
kpidFreeSpace = 0x1100 + 1
kpidClusterSize = 0x1100 + 2
kpidVolumeName = 0x1100 + 3

kpidLocalName = 0x1200
kpidProvider = 0x1200 + 1

kpidUserDefined = 0x10000