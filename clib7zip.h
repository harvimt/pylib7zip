#ifndef clib7zip
#define clib7zip

#if !CPLUSPLUS
#include <stdbool.h>
#endif
#include <wchar.h>

#ifndef _WIN32

#define __int64 long long int

#endif

typedef enum {
	PROP_INDEX_BEGIN,

	kpidPackSize = PROP_INDEX_BEGIN, //(Packed Size)
	kpidAttrib, //(Attributes)
	kpidCTime, //(Created)
	kpidATime, //(Accessed)
	kpidMTime, //(Modified)
	kpidSolid, //(Solid)
	kpidEncrypted, //(Encrypted)
	kpidUser, //(User)
	kpidGroup, //(Group)
	kpidComment, //(Comment)
	kpidPhySize, //(Physical Size)
	kpidHeadersSize, //(Headers Size)
	kpidChecksum, //(Checksum)
	kpidCharacts, //(Characteristics)
	kpidCreatorApp, //(Creator Application)
	kpidTotalSize, //(Total Size)
	kpidFreeSpace, //(Free Space)
	kpidClusterSize, //(Cluster Size)
	kpidVolumeName, //(Label)
	kpidPath, //(FullPath)
	kpidIsDir, //(IsDir)
	kpidSize, //(Uncompressed Size)

	PROP_INDEX_END
} PropertyIndexEnum;

typedef enum {
	ErrorCode_Begin,

	NO_ERROR = ErrorCode_Begin,
	UNKNOWN_ERROR,
	NOT_INITIALIZE,
	NEED_PASSWORD,
	NOT_SUPPORTED_ARCHIVE,

	ErrorCode_End
} ErrorCodeEnum;

//Types
typedef void c7z_Object;
typedef void c7z_ObjPtrArr; // Object Pointer Array, aka a list of c7z_Objects/C7ZipObjects
typedef void c7z_ArchiveItem;
typedef void c7z_InStream;
typedef void c7z_MultiVolume;
typedef void c7z_OutStream;
typedef void c7z_Archive;
typedef void c7z_Library;

//Object


//ArchiveItem
void free_C7ZipArchiveItem(c7z_ArchiveItem* self);
const wchar_t* c7zItm_GetFullPath(c7z_ArchiveItem* self);
unsigned __int64 c7zItm_GetSize(c7z_ArchiveItem* self);
bool c7zItm_IsDir(c7z_ArchiveItem* self);
bool c7zItm_IsEncrypted(c7z_ArchiveItem* self);
unsigned int C7zItm_GetArchiveIndex(c7z_ArchiveItem* self);
const wchar_t* c7zItm_GetFullPath(c7z_ArchiveItem* self);
bool c7zItm_GetUInt64Property(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, unsigned __int64 * val);
bool c7zItm_GetFileTimeProperty(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, unsigned __int64 * val);
bool c7zItm_GetStringProperty(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, wchar_t * buf, size_t buf_size);
bool c7zItm_GetBoolProperty(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, bool * val);

//InStream
c7z_InStream* create_c7zInSt_Filename(const char* filename);
const wchar_t* c7zInSt_GetExt(c7z_InStream* self);
int c7zInSt_Read(c7z_InStream* self, void *data, unsigned int size, unsigned int *processedSize);
int c7zInSt_Seek(c7z_InStream* self, __int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);
int c7zInSt_GetSize(c7z_InStream* self, unsigned __int64 * size);

//OutStream
int c7zOutSt_Write(c7z_OutStream* self, const void *data, unsigned int size, unsigned int *processedSize);
int c7zOutSt_Seek(c7z_OutStream* self, __int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);
int c7zOutSt_SetSize(c7z_OutStream* self, unsigned __int64 size);

//Archive
void free_C7ZipArchive(c7z_Archive* self);

void free_C7ZipArchive(c7z_Archive* self);

bool c7zArc_GetItemCount(c7z_Archive* self, unsigned int * pNumItems);

bool c7zArc_GetItemInfo(c7z_Archive* self, unsigned int index, c7z_ArchiveItem ** ppArchiveItem);
bool c7zArc_ExtractByIndex(c7z_Archive* self, unsigned int index, c7z_OutStream * pOutStream);
bool c7zArc_ExtractByIndexPW(c7z_Archive* self, unsigned int index, c7z_OutStream * pOutStream, const wchar_t* password);
bool c7zArc_ExtractByItem(c7z_Archive* self, const c7z_ArchiveItem * pArchiveItem, c7z_OutStream * pOutStream);

void c7zArc_Close(c7z_Archive* self);

bool c7zArc_GetUInt64Property(c7z_Archive* self, PropertyIndexEnum propertyIndex, unsigned __int64 * const val);
bool c7zArc_GetBoolProperty(c7z_Archive* self, PropertyIndexEnum propertyIndex, bool * const val);
bool c7zArc_GetStringProperty(c7z_Archive* self, PropertyIndexEnum propertyIndex, wchar_t * const buf, size_t buf_size);
bool c7zArc_GetFileTimeProperty(c7z_Archive* self, PropertyIndexEnum propertyIndex, unsigned __int64 * const val);

//Library
c7z_Library* create_C7ZipLibrary();
void free_C7ZipLibrary(c7z_Library* self);
bool c7zLib_Initialize(c7z_Library* self);
void c7zLib_Deinitialize(c7z_Library* self);
bool c7zLib_GetSupportedExts(c7z_Library* self, const wchar_t *** exts, unsigned int * size);
bool c7zLib_OpenArchive(c7z_Library* self, c7z_InStream* pInStream, c7z_Archive ** ppArchive);
bool c7zLib_IsInitialized(c7z_Library* self);
const ErrorCodeEnum c7zLib_GetLastError(c7z_Library* self);
#endif
