
import lib7zip

#print("Supported Extensions: %s" % ', '.join(lib7zip.get_supported_exts()))

archive = lib7zip.openarchive("C:\\Users\\gkmachine\\Downloads\\zips\\www-r.zip")
for i,item in enumerate(archive):
	print("%d  %s  %08X  %s" % (i, "D" if item.isdir else "F", item.crc, item.path))