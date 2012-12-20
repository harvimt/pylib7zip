#include <stdlib.h>
#include <stdio.h>
#include "clib7zip.h"
//#include <dlfcn.h>
#include <sys/types.h>
#include <linux/limits.h>
#include <string.h>

#include <dirent.h>

#ifndef _DIRENT_HAVE_D_TYPE
	#error "d_type not supported"
#endif

static const char* err_codes[] = {
	"NO_ERROR",
	"UNKNOWN_ERROR",
	"NOT_INITIALIZE",
	"NEED_PASSWORD",
	"NOT_SUPPORTED_ARCHIVE"
};

#define LAST_ERR err_codes[c7zLib_GetLastError(lib)]
const char* COALESCE(const char* x, const char* y){ return x?x:y; }
static c7z_Library* lib;

int openarchive(const char* path){
	c7z_InStream* instream = create_c7zInSt_Filename(path);

	if(instream == NULL){
		fprintf(stderr, "Error allocating input stream.\n");
		return 1;
	}

	const wchar_t* ext = c7zInSt_GetExt(instream);
	if(ext == NULL){
		fprintf(stderr, "Failed to get archive extension.");
		return 1;
	}
	//printf("File Extension: %ls\n", ext);
	


	c7z_Archive* archive = NULL;
	if(!c7zLib_OpenArchive(lib, instream, &archive) || archive == NULL){
		fprintf(stderr, "Error opening archive, err_code=%s.\n", LAST_ERR);
	}

	unsigned int item_count;
	if(!c7zArc_GetItemCount(archive, &item_count)){
		fprintf(stderr, "Error Getting Item Count, errcode=%s.\n", LAST_ERR);
		return 1;
	}

	//printf("Item Count: %d\n", item_count);

	c7z_ArchiveItem* arc_item;
	unsigned __int64 hash = 0xDEADBEEF;
	bool isdir;

	for(unsigned int i = 0; i < item_count; i += 1){
		if(!c7zArc_GetItemInfo(archive, i, &arc_item)){
			fprintf(stderr, "Error Getting Item info for item %d, errcode=%s\n", i, LAST_ERR);
			return 1;
		}

		//most properties need to be fetched with Get<type>Property functions
		if(!c7zItm_GetUInt64Property(arc_item, kpidCRC, &hash)){
			hash = 0xDEADBEEF;
		}

		//but some common properties have convenience functions
		isdir = c7zItm_IsDir(arc_item); //Note: you could use ...GetBoolProperty(..., kpidIsDir, ...) instead

		const wchar_t* path = c7zItm_GetFullPath(arc_item); //Note: similar, could use GetStringProperty intstead
		
		printf("%03u  %c  %08llX  %ls\n", i, isdir?'D':'F', hash, path);
	}

	c7zArc_Close(archive);

	free_C7ZipArchive(archive);

	return 0;
}


int main(){
	 lib = create_C7ZipLibrary();

	if(!c7zLib_Initialize(lib)){
		fprintf(stderr, "Failed to Intialize C7zip Library, %s\n", LAST_ERR);
		//fprintf(stderr, "dlerror(): %s\n", dlerror());
		return 1;
	}

	//printf("Supported Extensions: ");
	const wchar_t ** exts;
	unsigned int size;
	if(!c7zLib_GetSupportedExts(lib, &exts, &size)){
		fprintf(stderr, "Failed to get supported extensions, %s\n", LAST_ERR);
		return 1;
	}

	//for(size_t i = 0; i < size; i += 1){
		//printf("%ls,", exts[i]);
	//}

	//printf("\n");

	free(exts);

	const char BASE_PATH[] = "/media/Media/Games/Game Mods/oblivion/Bash Installers/";
	char path[PATH_MAX];
	strncpy(path, BASE_PATH, PATH_MAX);

	DIR *dp;
	struct dirent *ep;
	dp = opendir (BASE_PATH);

	if(dp != NULL){
		while( (ep = readdir(dp)) ){
			path[sizeof(BASE_PATH) -1 ] = '\0';
			if(ep->d_type == DT_REG){
				strncat(path,ep->d_name,PATH_MAX);
				if(openarchive(path)){
					return 1;
				}
			}
		}

		closedir(dp);
	}else{
		perror("Couldn't open the directory");
	}

	c7zLib_Deinitialize(lib);
	return 0;
}
