from __future__ import unicode_literals

import sys
import os, os.path

mod = 'c'
if mod == 'ctypes':
	import ctypes_lib7zip as lib7zip
	from ctyeps_lib7zip import NotSupportedArchive
elif mod == 'c':
	sys.path.append('./build/lib.linux-x86_64-2.7/')
	import lib7zip as lib7zip
	from lib7zip import NotSupportedArchive
elif mod == 'sub':
	import sub_lib7zip as lib7zip
	from sub_lib7zip import NotSupportedArchive


BASE_PATH = "/media/Media/Games/Game Mods/oblivion/Bash Installers/"

#print("Supported Extensions: %s" % ', '.join(lib7zip.get_supported_exts()))

for filename in os.listdir(BASE_PATH):
	filename = os.path.join(BASE_PATH, filename)
	if os.path.isdir(filename): continue

	print("::%s" % filename);

	try :
		archive = lib7zip.openarchive(filename);
	except NotSupportedArchive:
		print("Archive not supported");
		#sys.exit(1);
		continue

	for i,item in enumerate(archive):
		pass

		print((u"%04d  %s  %08X  %s" % (i, "D" if item.isdir else "F", item.crc or 0xdeadbeef, item.path)).encode('utf-8'));

