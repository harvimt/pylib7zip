#include <lib7zip.h>
#include <iostream>
#include <cwchar>
#include <cstring>
#include <cstdio>
#include "cpplib7z.h"

//#include <dlfcn.h>

#include <sys/types.h>
#include <linux/limits.h>
#include <string.h>
#include <dirent.h>

#include <boost/foreach.hpp>
#define foreach BOOST_FOREACH

static const char* err_codes[] =
{
	"NO_ERROR",
	"UNKNOWN_ERROR",
	"NOT_INITIALIZE",
	"NEED_PASSWORD",
	"NOT_SUPPORTED_ARCHIVE"
};

#define LAST_ERR err_codes[lib.GetLastError()]

inline const char* COALESCE(const char* x, const char* y){ return x?x:y; }

using namespace std;


int openarchive(C7ZipLibrary& lib, const char* path){

	printf("%s\n", path);

	//C7ZipInStreamFWrapper instream("C:\\Users\\gkmachine\\Downloads\\zips\\www-r.zip");
	C7ZipInStreamFWrapper instream(path);
	//C7ZipInStreamFWrapper instream("/media/Media/Games/Game Mods/oblivion/Bash Installers/Better dungeons BSA v4.5-40392.rar");
	//C7ZipInStreamFWrapper instream("/media/Media/Games/Game Mods/oblivion/Bash Installers/QTP3 Redimized.zip");

	//wcout << L"GetExt: " << instream.GetExt() << endl;

	unsigned __int64 size;
	if(instream.GetSize(&size) != 0) {
		cerr << "Error getting size of stream" << endl;
		return 1;
	}
	cout << "GetSize: " << size << endl;

	C7ZipArchive* archive = NULL;
	if(!lib.OpenArchive(&instream, &archive)) {
		cerr << "Failed to Open Archive, errcode="<< LAST_ERR << endl;
		return 1;
	}
	printf("Successfully opened Archive!");

	unsigned int item_count;
	if(!archive->GetItemCount(&item_count)) {
		cerr << "Failed to Get Item Count, errcode="<< LAST_ERR << endl;
		return 1;
	}

	cout << "Item Count: " << item_count << endl;

	//unsigned __int64 filesize = 0x0;
	unsigned __int64 checksum = 0xDEADBEEF;
	bool isdir;
	for(unsigned int i = 0; i < item_count; i += 1) {
		C7ZipArchiveItem* item = NULL;
		if(!archive->GetItemInfo(i, &item) && item != NULL) {
			cerr << "Failed to GetItemInfo for item, #" << i << ", errcode=" << LAST_ERR << endl;
			return 1;
		}

		//Get IsDir
		isdir = item->IsDir();
		(void)isdir;

		const wstring& path = item->GetFullPath();
		if(!item->GetUInt64Property(kpidCRC, checksum)) {
			checksum = 0xDEADBEEF;
		}
		(void)path;

		#if __WIN32
			wprintf(L"%03u  %c  %08llX  %ls\n", i, isdir?L'D':L'F', checksum, path.c_str());
		#else
			printf("%03u  %c  %08llX  %ls\n", i, isdir?'D':L'F', checksum, path.c_str());
		#endif
	}

	archive->Close();
	delete archive;

	return 0;
}


int main(){
	C7ZipLibrary lib;
	if(!lib.Initialize()) {
		cerr << "Failed to Initialize Lib7Zip Library" << endl;
		//cerr << "dlerror(): " << dlerror() << endl;
		return 1;
	}

	vector<wstring> supported_exts;
	if(!lib.GetSupportedExts(supported_exts)) {
		cerr << "Failed to GetSupportedExts, errcode=" << LAST_ERR << endl;
		return 1;
	}
	//cout << "Supported Extensions: ";
	//foreach(wstring ext, supported_exts) {
		//wcout << ext << L",";
	//}
	//cout << endl;

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
				if(openarchive(lib, path)){
					//return 1;
				}
			}
		}

		closedir(dp);
	}else{
		perror("Couldn't open the directory");
	}

	lib.Deinitialize();
	return 0;
}
