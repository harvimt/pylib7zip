
import sys
sys.path.append('./build/lib.linux-x86_64-2.7/')

import lib7zip
#lib7zip.system("ls")

#print("hello");
archive = lib7zip.openarchive("/media/Media/Games/Game Mods/oblivion/Bash Installers/(MBP) 2ched 180 fix.7z");
print("opened archive successfully");

print("There are %d item(s) in the archive." % len(archive));

for i in range(0,len(archive)):
	item = archive[i]
	print("%d  %s%s  %d  %s" % (i, "D" if item.isdir else "F", "E" if item.isencrypted else "U", item.size, item.path));

archive.close();

#for item in archive:
	#pass

#("/media/Media/Games/Game Mods/oblivion/Bash Installers/Better dungeons BSA v4.5-40392.rar");
#("/media/Media/Games/Game Mods/oblivion/Bash Installers/QTP3 Redimized.zip");

