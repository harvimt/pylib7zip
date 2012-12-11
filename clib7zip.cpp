#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <cwchar>

#include <lib7zip.h>
#include "cpplib7z.h"

extern "C" {
#include "clib7zip.h"

//Object
c7z_Object* create_C7zipObject() {
	return static_cast<c7z_Object*>(new C7ZipObject);
}
void free_c7z_Object(c7z_Object* self){
	delete static_cast<C7ZipObject*>(self);
}

//ObjectPtrArray
c7z_ObjPtrArr* create_c7z_ObjPtrArr(){
	return static_cast<c7z_ObjPtrArr*>(new C7ZipObjectPtrArray);
}

c7z_ObjPtrArr* create_c7z_ObjPtrArr1(bool auto_release){
	return static_cast<c7z_ObjPtrArr*>(new C7ZipObjectPtrArray(auto_release));
}

void free_c7z_ObjPtrArr(c7z_ObjPtrArr* self){
	delete static_cast<C7ZipObjectPtrArray*>(self);
}

void c7zOPArr_clear(c7z_ObjPtrArr* self){
	return static_cast<C7ZipObjectPtrArray*>(self)->clear();
}

size_t c7zOPArr_GetSize(c7z_ObjPtrArr* self){
	return static_cast<C7ZipObjectPtrArray*>(self)->size();
}

c7z_Object* c7zOPArr_GetItemAt(c7z_ObjPtrArr* self, size_t index){
	return (*static_cast<C7ZipObjectPtrArray*>(self))[index];
}

// Archive Item
void free_C7ZipArchiveItem(c7z_ArchiveItem* self){
	delete static_cast<C7ZipArchiveItem*>(self);
}

const wchar_t* c7zItm_GetFullPath(c7z_ArchiveItem* self){
	return static_cast<C7ZipArchiveItem*>(self)->GetFullPath().c_str();
}

unsigned __int64 c7zItm_GetSize(c7z_ArchiveItem* self){
	return static_cast<C7ZipArchiveItem*>(self)->GetSize();
}

bool c7zItm_IsDir(c7z_ArchiveItem* self){
	return static_cast<C7ZipArchiveItem*>(self)->IsDir();
}

bool c7zItm_IsEncrypted(c7z_ArchiveItem* self){
	return static_cast<C7ZipArchiveItem*>(self)->IsEncrypted();
}

unsigned int c7zItm_GetArchiveIndex(c7z_ArchiveItem* self){
	return static_cast<C7ZipArchiveItem*>(self)->GetArchiveIndex();
}

bool c7zItm_GetUInt64Property(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, unsigned __int64 * const val){
	return static_cast<C7ZipArchiveItem*>(self)->GetUInt64Property(static_cast<lib7zip::PropertyIndexEnum>(propertyIndex), *val);
}

bool c7zItm_GetFileTimeProperty(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, unsigned __int64 * const val){
	return static_cast<C7ZipArchiveItem*>(self)->GetFileTimeProperty(static_cast<lib7zip::PropertyIndexEnum>(propertyIndex), *val);
}

bool c7zItm_GetStringProperty(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, wchar_t * const buf, size_t buf_size){
	wstring val;
	if(!static_cast<C7ZipArchiveItem*>(self)->GetStringProperty(static_cast<lib7zip::PropertyIndexEnum>(propertyIndex),  val)){
		return false;
	}
	
	if(val.length() > buf_size){
		return false;
	}
	
	wcsncpy(buf, val.c_str(), buf_size);

	return true;
}

bool c7zItm_GetBoolProperty(c7z_ArchiveItem* self, PropertyIndexEnum propertyIndex, bool * val){
	return static_cast<C7ZipArchiveItem*>(self)->GetBoolProperty(static_cast<lib7zip::PropertyIndexEnum>(propertyIndex), *val);
}

// InStream

c7z_InStream* create_c7zInSt_Filename(const char* filename){
	C7ZipInStreamFWrapper instream(filename);
	C7ZipInStream* r = & instream;
	return static_cast<c7z_InStream*>(r);
}

c7z_InStream* create_c7zInSt_FD(FILE* fd, wchar_t* ext){
	C7ZipInStreamFWrapper instream(fd, ext);
	C7ZipInStream* r = &instream;
	return static_cast<c7z_InStream*>(r);
}

const wchar_t* c7zInSt_GetExt(c7z_InStream* self){
	printf("Got to GetExt!\n");
	const wstring wext = static_cast<C7ZipInStream*>(self)->GetExt();
	//const wchar_t* ext = 
	//printf("GetExt: %ls\n", wext.c_str());
	//return ext;
	return L".ext";
}

int c7zInSt_Read(c7z_InStream* self, void* data, unsigned int size, unsigned int *processedSize){
	return static_cast<C7ZipInStream*>(self)->Read(data, size, processedSize);
}

int c7zInSt_Seek(c7z_InStream* self, __int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition){
	return static_cast<C7ZipInStream*>(self)->Seek(offset, seekOrigin, newPosition);
}

int c7zInSt_GetSize(c7z_InStream* self, unsigned __int64 * size){
	return static_cast<C7ZipInStream*>(self)->GetSize(size);
}

//Out Streem
int c7zOutSt_Write(c7z_OutStream* self, const void *data, unsigned int size, unsigned int *processedSize){
	return static_cast<C7ZipOutStream*>(self)->Write(data, size, processedSize);
}
int c7zOutSt_Seek(c7z_OutStream* self, __int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition){
	return static_cast<C7ZipOutStream*>(self)->Seek(offset, seekOrigin, newPosition);
}

int c7zOutSt_SetSize(c7z_OutStream* self, unsigned __int64 size){
	return static_cast<C7ZipOutStream*>(self)->SetSize(size);
}

//Archive
void free_C7ZipArchive(c7z_Archive* self){
	delete static_cast<C7ZipArchive*>(self);
}

bool c7zArc_GetItemCount(c7z_Archive* self, unsigned int * pNumItems){
	return static_cast<C7ZipArchive*>(self)->GetItemCount(pNumItems);
}

bool c7zArc_GetItemInfo(c7z_Archive* self, unsigned int index, c7z_ArchiveItem ** ppArchiveItem){
	//static_cast<void*>(ppArchiveItem);
	C7ZipArchiveItem* item;

	if(!static_cast<C7ZipArchive*>(self)->GetItemInfo(index, &item)){
		return false;
	}

	*ppArchiveItem = static_cast<c7z_ArchiveItem*>(item);
	return true;
}

bool c7zArc_ExtractByIndex(c7z_Archive* self, unsigned int index, c7z_OutStream * pOutStream){
	return static_cast<C7ZipArchive*>(self)->Extract(index, static_cast<C7ZipOutStream*>(pOutStream));
}

bool c7zArc_ExtractByIndexPW(c7z_Archive* self, unsigned int index, c7z_OutStream * pOutStream, const wchar_t* password){
	const wstring pwd(password);
	return static_cast<C7ZipArchive*>(self)->Extract(index, static_cast<C7ZipOutStream*>(pOutStream), pwd);
}

bool c7zArc_ExtractByItem(c7z_Archive* self, const c7z_ArchiveItem * pArchiveItem, c7z_OutStream * pOutStream){
	return static_cast<C7ZipArchive*>(self)->Extract(static_cast<const C7ZipArchiveItem*>(pArchiveItem), static_cast<C7ZipOutStream*>(pOutStream));
}

void c7zArc_Close(c7z_Archive* self){
	static_cast<C7ZipArchive*>(self)->Close();
}

bool c7zArc_GetUInt64Property(c7z_Archive* self, PropertyIndexEnum propertyIndex, unsigned __int64 * const val){
	return static_cast<C7ZipArchive*>(self)->GetUInt64Property( static_cast<lib7zip::PropertyIndexEnum>(propertyIndex), *val);
}

bool c7zArc_GetBoolProperty(c7z_Archive* self, PropertyIndexEnum propertyIndex, bool * const val){
	return static_cast<C7ZipArchive*>(self)->GetBoolProperty( static_cast<lib7zip::PropertyIndexEnum>(propertyIndex), *val);
}

bool c7zArc_GetStringProperty(c7z_Archive* self, PropertyIndexEnum propertyIndex, wchar_t * const buf, size_t buf_size){
	wstring val;
	if(!static_cast<C7ZipArchive*>(self)->GetStringProperty(static_cast<lib7zip::PropertyIndexEnum>(propertyIndex),  val)){
		return false;
	}

	if(val.length() > buf_size){
		return false;
	}
	
	wcsncpy(buf, val.c_str(), buf_size);

	return true;
}
bool c7zArc_GetFileTimeProperty(c7z_Archive* self, PropertyIndexEnum propertyIndex, unsigned __int64 * const val){
	return static_cast<C7ZipArchive*>(self)->GetFileTimeProperty( static_cast<lib7zip::PropertyIndexEnum>(propertyIndex), *val);
}

//Library
c7z_Library* create_C7ZipLibrary(){
	return static_cast<c7z_Library*>(new C7ZipLibrary());
}

void free_C7ZipLibrary(c7z_Library* self){
	delete static_cast<C7ZipLibrary*>(self);
}

bool c7zLib_Initialize(c7z_Library* self){
	return static_cast<C7ZipLibrary*>(self)->Initialize();
}

void c7zLib_Deinitialize(c7z_Library* self){
	return static_cast<C7ZipLibrary*>(self)->Deinitialize();
}

bool c7zLib_GetSupportedExts(c7z_Library* self, const wchar_t*** exts, unsigned int * size){
	WStringArray in;
	const bool r = static_cast<C7ZipLibrary*>(self)->GetSupportedExts(in);
	*size = in.size();
	*exts = static_cast<const wchar_t**>(malloc( sizeof(wchar_t*) * in.size() ));

	size_t i = 0;
	WStringArray::iterator it;
	for(it = in.begin(), i = 0; it != in.end(); it++, i++){
		wstring ext = *it;
		(*exts)[i] = ext.c_str();
	}

	return r;
}

bool c7zLib_OpenArchive(c7z_Library* self, c7z_InStream* pInStream, c7z_Archive ** ppArchive){
	C7ZipArchive* archive;
	bool r = static_cast<C7ZipLibrary*>(self)->OpenArchive(static_cast<C7ZipInStream*>(pInStream), &archive);
	*ppArchive = static_cast<c7z_Archive*>(archive);
	return r;
}

//TOOD: const C7ZipObjectPtrArray * c7zLib_GetInternalObjectsArray();

bool c7zLib_IsInitialized(c7z_Library* self){
	return static_cast<C7ZipLibrary*>(self)->IsInitialized();
}

const ErrorCodeEnum c7zLib_GetLastError(c7z_Library* self) {
	return static_cast<ErrorCodeEnum>( static_cast<C7ZipLibrary*>(self)->GetLastError() );
}

} //end extern "C"
