# -*- coding=utf-8 -*-
from __future__ import unicode_literals, absolute_import
from future.builtins import *

from functools import partial
from glob import glob
import io
import shutil
import os
from tempfile import mkdtemp
import pytest
from collections import namedtuple
import logging

from lib7zip import *
log = logging.getLogger('lib7zip')

simple_archives = ('tests/simple.7z', 'tests/simple.zip')
@pytest.fixture(scope='session')
def tmp_dir(request):
	path = mkdtemp()
	request.addfinalizer(partial(shutil.rmtree, path))
	return path

_IX = namedtuple('ArchiveItemEx', ('isdir', 'crc', 'contents'))
def IX(isdir=False, crc=None, contents=''):
	#return _IX(isdir, crc, contents.encode('utf8') if contents is not None else None)
	return _IX(isdir, crc, contents)
J = os.path.join

COMPLEX_MD = {
	J('complex','articles'): IX(True),
	J('complex','articles','the definate article.txt'): IX(False, 0x3C456DE6, 'the'),
	J('complex','articles','the indefinate article.txt'): IX(False, 0xE8B7BE43, 'a'),
	J('complex','goodbye.txt'): IX(False, 0x3078A778, 'Goodbye!'),
	J('complex','hello.txt'): IX(False, 0x9D2ACC56, 'Hello!'),
	#J('complex','unicode.txt'): IX(False, 0x226F311C, 'Úñï¢ðÐê †ê§†!'),
	J('complex','empty.txt'): IX(False, None, ''),
	J('complex','empty'): IX(True),
	J('complex'): IX(True),
}

def test_complex():
	log.debug('test_complex()')
	with Archive('tests/complex.7z') as archive:
		for item in archive:
			log.debug(item.path)
			try:
				md = COMPLEX_MD[item.path]
			except KeyError as ex:
				log.warn('key %s not present', ex.args[0])
				continue
				
			assert item.isdir == md.isdir
			if md.crc is None:
				assert item.crc is None
			else:
				assert item.crc == md.crc

			if not item.isdir:
				assert item.contents.decode('utf-8') == md.contents
		logging.debug('done iterating archives')

def test_extract_dir_complex(tmp_dir):
	with Archive('tests/complex.7z') as archive:
		archive.extract(tmp_dir)
	
	for path, md in COMPLEX_MD.items():
		if md.contents:
			with open(os.path.join(tmp_dir, path), encoding='utf-8') as f:
				file_contents = f.read()
				#if 'unicode' in path:
				#	import pdb; pdb.set_trace()
				assert file_contents == md.contents

@pytest.mark.parametrize('path', simple_archives)
def test_extract_stream(path):
	with Archive(path) as archive:
		stream = io.BytesIO()
		archive[0].extract(stream)
		assert stream.getvalue() == b'Hello World!\n'

@pytest.mark.parametrize('path', simple_archives)
def test_extract_dir(path, tmp_dir):
	with Archive(path) as archive:
		archive.extract(tmp_dir)
		
	with open(os.path.join(tmp_dir, 'hello.txt'), 'rb') as f:
		assert f.read() == b'Hello World!\n'

@pytest.mark.xfail(run=False)
def test_extract_with_pass():
	with Archive('tests/simple_crypt.7z') as archive:
		stream = io.BytesIO()
		assert archive[0].path == 'hello.txt'
		archive[0].extract(stream, password='password')
		assert stream.getvalue() == b'Hello World!\n'

@pytest.mark.xfail(run=False)
def test_extract_with_pass_dir(tmp_dir):
	with Archive('tests/simple crypt.7z', password='password') as archive:
		archive.extract(tmp_dir)

	with open(os.path.join(tmp_dir, 'hello.txt'), 'rb') as f:
		assert f.read() == b'Hello World!\n'

@pytest.mark.xfail(run=False)
def test_extract_badpass():
	with Archive('tests/simple crypt.7z') as archive:
		stream = io.BytesIO()
		with pytest.raises(Exception):  # TODO catch correct exception
			archive[0].extract(stream, password='notthepass')
