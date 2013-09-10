from functools import partial
from glob import glob
import io

from lib7zip import *

def test_getinfo():
	for arc_path in glob(r'D:\Games\Game Mods\oblivion\Bash Installers\*'):
		if not arc_path.endswith(('.7z', '.zip', '.rar')):
			continue
		
		print(arc_path)

		with Archive(arc_path) as archive:
			for item in archive:
				#print(item.isdir)
				print(
					item.isdir,
					item.path.encode('ascii', errors='backslashescape').decode('ascii'),
					'0x%08x' % item.crc if item.crc else '#NOCRC#',
				)

		break

def test_extract():
	with Archive('simple.7z') as archive:
		stream = io.BytesIO()
		archive[0].extract(stream)
		assert stream.getvalue() == b'Hello World!\n'

def test_extract_dir():
	with Archive('simple.7z') as archive:
		archive.extract('out_dir')
	
		
#test_getinfo()
#test_extract()
test_extract_dir()