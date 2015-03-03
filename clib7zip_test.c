#include <stdint.h>
#include <wchar.h>
#include "windowsdefs.h"
#include "clib7zip.h"
#include <dlfcn.h>
#include <assert.h>

_GetNumberOfFormats GetNumberOfFormats;
_GetNumberOfMethods GetNumberOfMethods;
_GetMethodProperty GetMethodProperty;
_GetHandlerProperty2 GetHandlerProperty2;
_CreateObject CreateObject;

int main(){
#if WIN32
#define dlopen_rtld_now LoadLibrary
#define dlsym GetProcAddress
//TODO dlerror
const char *lib_paths[] = {
    "C:\\Program Files\\7-Zip\\7z.dll",
    "C:\\Program Files (x86)\\7-Zip\\7z.dll"
};
HMODULE lib;
#else
#define dlopen_rtld_now(path) dlopen(path, RTLD_NOW)
const char *lib_paths[] = {
    "/usr/lib/p7zip/7z.so"
};
void* lib;
#endif
    unsigned int i;
    printf("Trying to open 7zip library from a default path\n");
    for(i = 0; i < sizeof(lib_paths) / sizeof(char*); i += 1){
        printf("Trying to open 7zip library: %s\n", lib_paths[i]);
        lib = dlopen_rtld_now(lib_paths[i]);
        if(lib != NULL){
            puts("Loaded");
            break;
        }
    }
    if (lib == NULL){
        puts("NULL FAIL"); //FIXME
        return 1;
    }

    GetNumberOfFormats = (_GetNumberOfFormats) dlsym(lib, "GetNumberOfFormats");
    if(GetNumberOfFormats == NULL){
        puts("NULL FAIL"); // FIXME
        return 1;
    }

    GetHandlerProperty2 = (_GetHandlerProperty2) dlsym(lib, "GetHandlerProperty2");
    if(GetHandlerProperty2 == NULL){
        puts("NULL FAIL"); // FIXME
        return 1;
    }

    CreateObject = (_CreateObject) dlsym(lib, "CreateObject");
    if(CreateObject == NULL){
        puts("NULL FAIL"); // FIXME
        return 1;
    }
    /*
    puts("Initializing...");
    CLIB7ZIP* lib = init_clib7zip(NULL);

    FILE* file = fopen("abc.7z", "rb");
    printf("file=%p\n", file);
    IInStream* stream = create_instream_from_file(file);
    assert(stream != NULL);
    IInArchive* archive = create_archive(L"7z");
    assert(archive != NULL);

    puts("Opening...");
    archive_open(archive, stream, NULL, NULL, NULL, NULL, NULL);
    puts("...Opened");

    uint32_t num_items;
    uint32_t i;
    PROPVARIANT* pvar = create_propvariant();

    if(archive_get_num_items(archive, &num_items) != S_OK){
        puts("Error"); return 1;
    }
    printf("num_items=%d\n", num_items);
    for(i = 0; i < num_items; i += 1){
        assert(archive_get_item_property_pvar(archive, i, kpidCRC, pvar) == S_OK);
        assert(pvar->vt == VT_UI4);
        printf("crc=%lx\n", pvar->ulVal);

        assert(archive_get_item_property_pvar(archive, i, kpidPath, pvar) == S_OK);
        assert(pvar->vt == VT_BSTR);
        printf("path=%ls\n", pvar->bstrVal);
    }

    destroy_propvariant(pvar);

    puts("Closing...");
    archive_close(archive);
    archive_release(archive);
    fclose(file);
    puts("...Closed");

    teardown_clib7zip(lib);
    */
    return 0;
}
