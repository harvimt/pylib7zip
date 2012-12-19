#!/usr/bin/env python2

from ctypes import *

dll7z = cdll.LoadLibrary("libc7zip.dll")

#initialize
lib = c_void_p()
lib = dll7z.create_C7ZipLibrary();
dll7z.c7zLib_Initialize(lib);

num_exts = c_ulong();
ext_array = pointer(c_wchar_p())
dll7z.c7zLib_GetSupportedExts(lib, byref(ext_array), byref(num_exts))

print("Supported Extensions: " + ', '.join(str(ext_array[i]) for i in range(num_exts.value)))

instream = dll7z.create_c7zInSt_Filename("C:\\Users\\gkmachine\\Downloads\\zips\\www-r.zip")
ext = c_wchar_p(dll7z.c7zInSt_GetExt(instream))
archive = c_void_p();
dll7z.c7zLib_OpenArchive(lib, instream, byref(archive))
print("Opened file, got extension %s" % ext.value)

item_count = c_ulong()
dll7z.c7zArc_GetItemCount(archive, byref(item_count))
print("%d items in archive" % item_count.value)
for i in range(item_count.value):
	item = c_void_p()
	dll7z.c7z_Arc_GetItemInfo(archive, i, byref(item)
	pass

dll7z.c7zLib_Deinitialize(lib);
dll7z.free_C7ZipLibrary(lib);
