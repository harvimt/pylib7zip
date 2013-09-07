from functools import partial
from glob import glob

from lib7zip import *
from lib7zip.py7ziptypes import kpidCRC, kpidPath

def test_getinfo():

	for arc_path in glob(r'D:\Games\Game Mods\oblivion\Bash Installers\*'):
		if not arc_path.endswith(('.7z', '.zip', '.rar')):
			continue
		
		print(arc_path)

		with Archive(arc_path) as archive:
			for isdir, path, crc32 in archive:
				pass
				#print(isdir, path.encode(errors='backslashescape').decode('ascii'), crc32)
		#break

def test_extract():
	with Archive('simple.7z') as archive:
		archive.extract()
		
#test_getinfo()
test_extract()