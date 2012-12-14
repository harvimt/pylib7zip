
import sys, os, os.path
sys.path.append('./build/lib.linux-x86_64-2.7/')

import lib7zip
from lib7zip import NotSupportedArchive
#lib7zip.system("ls")

BASE_PATH = "/media/Media/Games/Game Mods/oblivion/Bash Installers/"

#archive = lib7zip.openarchive("foo");

#print("hello");
for filename in os.listdir(BASE_PATH):
	filename = os.path.join(BASE_PATH, filename)
	#if not filename.endswith('.rar'): continue
	if os.path.isdir(filename): continue

	print("opening %s" % filename);

	try :
		archive = lib7zip.openarchive(filename);
	except NotSupportedArchive:
		print("Archive not supported");
		sys.exit(1);
		continue

	print("opened archive successfully");

	print("There are %d item(s) in the archive." % len(archive));

	for item in archive:
	#for i in range(0,len(archive)):
		#item = archive[i]

		print("%d  %s%s  % 10d  %08X  %s" % (item.index, "D" if item.isdir else "F", "E" if item.isencrypted else "U", item.size, item.crc or 0x0, item.path));

	archive.close();

#for item in archive:
	#pass

#("/media/Media/Games/Game Mods/oblivion/Bash Installers/Better dungeons BSA v4.5-40392.rar");
#("/media/Media/Games/Game Mods/oblivion/Bash Installers/QTP3 Redimized.zip");

