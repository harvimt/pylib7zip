#include <dlfcn.h>
#include <stdlib.h>
#include <stdio.h>
#include "clib7zip.h"

static const char* err_codes[] = {
	"NO_ERROR",
	"UNKNOWN_ERROR",
	"NOT_INITIALIZE",
	"NEED_PASSWORD",
	"NOT_SUPPORTED_ARCHIVE"
};

#define LAST_ERR err_codes[c7zLib_GetLastError(lib)]
const char* COALESCE(const char* x, const char* y){ return x?x:y; }

int main(int argc, char** argv){
	c7z_Library* lib = create_C7ZipLibrary();
	if (lib == NULL){
		fprintf(stderr, "Failed to allocate C7zip Library\n");
		fprintf(stderr, "dlerror() = %s", COALESCE(dlerror(), "NULL"));
		return 1;
	}

	if(!c7zLib_Initialize(lib)){
		fprintf(stderr, "Failed to Intialize C7zip Library, %s\n", LAST_ERR);
		return 1;
	}

	printf("Supported Extensions: ");
	const wchar_t ** exts;
	unsigned int size;
	if(!c7zLib_GetSupportedExts(lib, &exts, &size)){
		fprintf(stderr, "Failed to get supported extensions, %s\n", LAST_ERR);
		return 1;
	}

	for(size_t i = 0; i < size; i += 1){
		printf("%ls,", exts[i]);
	}

	printf("\n");

	free(exts);

	c7z_InStream* instream = create_c7zInSt_Filename("/media/Media/Games/Game Mods/oblivion/Bash Installers/(MBP) 2ched 180 fix.7z");
	if(instream == NULL){
		fprintf(stderr, "Error allocating input stream.\n");
		return 1;
	}

	const wchar_t* ext = c7zInSt_GetExt(instream);
	if(ext == NULL){
		fprintf(stderr, "Failed to get archive extension.");
		return 1;
	}
	printf("File Extension: %ls\n", ext);

	c7z_Archive* archive;
	if(!c7zLib_OpenArchive(lib, instream, &archive)){
		fprintf(stderr, "Error opening archive, err_code=%s.\n", LAST_ERR);
	}

	unsigned int item_count;
	if(!c7zArc_GetItemCount(archive, &item_count)){
		fprintf(stderr, "Error Getting Item Count, errcode=%s.\n", LAST_ERR);
		return 1;
	}

	printf("Item Count: %d\n", item_count);

	c7z_ArchiveItem* arc_item;
	unsigned __int64 hash;
	bool isdir;

	for(unsigned int i = 0; i < item_count; i += 1){
		printf("Item #%u:\n", i);
		if(!c7zArc_GetItemInfo(archive, i, &arc_item)){
			fprintf(stderr, "Error Getting Item info for item %d, errcode=%s\n", i, LAST_ERR);
			return 1;
		}

		if(!c7zItm_GetUInt64Property(arc_item, kpidChecksum, &hash)){
			fprintf(stderr, "Error Getting checksum for item %d, errcode=%s\n", i, LAST_ERR);
			return 1;
		}

		isdir = c7zItm_IsDir(arc_item); //Note: you could use ...GetBoolProperty(..., kpidIsDir, ...) instead


		const wchar_t* path = c7zItm_GetFullPath(arc_item); //Note: similar, could use GetStringProperty intstead,
		                                                    //but you have to send it a buffer if you do.

		printf("path=%ls\nisdir=%d\nhash %lx\n\n", path, isdir, hash);

		free_C7ZipArchiveItem(arc_item);
	}

	c7zArc_Close(archive);
	free_C7ZipArchive(archive);

	c7zLib_Deinitialize(lib);
	return 0;
}
