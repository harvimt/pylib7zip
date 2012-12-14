#include <dlfcn.h>
#include <lib7zip.h>
#include <iostream>
#include <cwchar>
#include <cstring>
#include <cstdio>
#include "cpplib7z.h"

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

int main()
{

	C7ZipLibrary lib;
	if(!lib.Initialize()) {
		cerr << "Failed to Initialize Lib7Zip Library, errcode=" << LAST_ERR << endl;
		cerr << COALESCE(dlerror(), "NO ERROR") << endl;
		return 1;
	}

	vector<wstring> supported_exts;
	if(!lib.GetSupportedExts(supported_exts)) {
		cerr << "Failed to GetSupportedExts, errcode=" << LAST_ERR << endl;
		return 1;
	}
	cout << "Supported Extensions: ";
	foreach(wstring ext, supported_exts) {
		wcout << ext << L",";
	}
	cout << endl;

	C7ZipInStreamFWrapper instream("/media/Media/Games/Game Mods/oblivion/Bash Installers/(MBP) 2ched 180 fix.7z");
	//C7ZipInStreamFWrapper instream("/media/Media/Games/Game Mods/oblivion/Bash Installers/Better dungeons BSA v4.5-40392.rar");
	//C7ZipInStreamFWrapper instream("/media/Media/Games/Game Mods/oblivion/Bash Installers/QTP3 Redimized.zip");

	wcout << L"GetExt: " << instream.GetExt() << endl;

	unsigned __int64 size;
	if(instream.GetSize(&size) != S_OK) {
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

	unsigned __int64 filesize = 0x0;
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

		//or with GetBoolProperty(...)
		if(!item->GetBoolProperty(kpidIsDir, isdir)) {
			cerr << "Failed to get IsDir for item, #" << i << ", errcode=" << LAST_ERR << endl;
		}

		const wstring& path = item->GetFullPath();
		if(!item->GetUInt64Property(kpidCRC, checksum)) {
			checksum = 0xDEADBEEF;
			//cerr << "Failed to get checksum for item, #" << i << ", errcode=" << LAST_ERR << endl;
		}

		//filesize = item->GetSize();
		if(!item->GetUInt64Property(kpidSize, filesize)) {
			cerr << "Failed to get size for item, #" << i << ", errcode=" << LAST_ERR << endl;
		}

		printf("%u\t%s\t%08llX\t%llu\t%ls\n", i, isdir?"D":"F", checksum, filesize, path.c_str());

		//delete item;
	}

	archive->Close();
	delete archive;

	lib.Deinitialize();
	return 0;
}
