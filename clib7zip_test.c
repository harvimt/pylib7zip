#include "clib7zip.h"
#include "7zip/PropID.h"
#include <assert.h>

#define WCHAR_T_BUF_SIZE(buf) ((sizeof(buf) / sizeof(wchar_t)) - 1)

int main(){
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
    wchar_t path[128];
    uint64_t crc;

    if(archive_get_num_items(archive, &num_items) != S_OK){
        puts("Error"); return 1;
    }
    printf("num_items=%d\n", num_items);
    for(i = 0; i < num_items; i += 1){
        if(archive_get_item_property_str(archive, i, kpidPath,
                path, WCHAR_T_BUF_SIZE(path)) != S_OK){
            puts("Error"); return 1;
        }
        if(archive_get_item_property_uint64(archive, i, kpidCRC, &crc) != S_OK){
            puts("Error"); return 1;
        }
        printf("path=%ls, crc=%lx\n", path, crc);
    }

    puts("Closing...");
    archive_close(archive);
    archive_release(archive);
    fclose(file);
    puts("...Closed");

    teardown_clib7zip(lib);
    return 0;
}
