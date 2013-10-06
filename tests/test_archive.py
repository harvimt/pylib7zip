from functools import partial
from glob import glob
import io
import shutil
import os
from tempfile import mkdtemp

from lib7zip import *

def test_getinfo():
	print(os.getcwd())
	with Archive('tests/complex.7z') as archive:
		for item in archive:
			print(
				item.isdir,
				item.path.encode('ascii', errors='backslashescape').decode('ascii'),
				'0x%08x' % item.crc if item.crc else '#NOCRC#',
			)

def test_extract():
	with Archive('tests/simple.7z') as archive:
		stream = io.BytesIO()
		archive[0].extract(stream)
		assert stream.getvalue() == b'Hello World!\n'

def test_extract_dir():
	out_dir = mkdtemp()
	
	with Archive('tests/simple.7z') as archive:
		archive.extract(out_dir)
		
	with open(os.path.join(out_dir, 'hello.txt'), 'rb') as f:
		assert f.read() == b'Hello World!\n'
	
	shutil.rmtree(out_dir)

#test_getinfo()
#test_extract()
#test_extract_dir()