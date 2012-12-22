#!/usr/bin/env python2

exe7z = '/usr/bin/7za'
import subprocess

import sys
if sys.version_info.major < 3:
	range = xrange
else:
	unicode = str
	long = int


class UnknownError(Exception): pass
class NotInitialize(Exception): pass
class NeedPassword(Exception): pass
class NotSupportedArchive(Exception): pass

import chardet
from collections import namedtuple

#copied from bolt.py part of Wrye Bash

# Unicode ---------------------------------------------------------------------
#--decode unicode strings
#  This is only useful when reading fields from mods, as the encoding is not
#  known.  For normal filesystem interaction, these functions are not needed
encodingOrder = (
	'ascii',    # Plain old ASCII (0-127)
	'gbk',      # GBK (simplified Chinese + some)
	'cp932',    # Japanese
	'cp949',    # Korean
	'cp1252',   # English (extended ASCII)
	'utf8',
	'cp500',
	'UTF-16LE',
	'mbcs',
	)

_encodingSwap = {
	# The encoding detector reports back some encodings that
	# are subsets of others.  Use the better encoding when
	# given the option
	# 'reported encoding':'actual encoding to use',
	'GB2312': 'gbk',        # Simplified Chinese
	'SHIFT_JIS': 'cp932',   # Japanese
	'windows-1252': 'cp1252',
	'windows-1251': 'cp1251',
	}

def _getbestencoding(text):
	"""Tries to detect the encoding a bitstream was saved in.  Uses Mozilla's
	   detection library to find the best match (heurisitcs)"""
	result = chardet.detect(text)
	encoding,confidence = result['encoding'],result['confidence']
	encoding = _encodingSwap.get(encoding,encoding)
	## Debug: uncomment the following to output stats on encoding detection
	#print
	#print '%s: %s (%s)' % (repr(text),encoding,confidence)
	return encoding,confidence

#copied from bolt.py
def _unicode(text,encoding=None,avoidEncodings=()):
	if isinstance(text,unicode) or text is None: return text
	# Try the user specified encoding first
	if encoding:
		try: return unicode(text,encoding)
		except UnicodeDecodeError: pass
	# Try to detect the encoding next
	encoding,confidence = _getbestencoding(text)
	if encoding and confidence >= 0.55 and (encoding not in avoidEncodings or confidence == 1.0):
		try: return unicode(text,encoding)
		except UnicodeDecodeError: pass
	# If even that fails, fall back to the old method, trial and error
	for encoding in encodingOrder:
		try: return unicode(text,encoding)
		except UnicodeDecodeError: pass
	raise UnicodeDecodeError(u'Text could not be decoded using any method')

ArchiveItem = namedtuple('Archive', ('isdir','crc','path'))

class Archive(object):
	def __init__(self, filename):
		#pass commandline args in as tuple
		#get stdout as pipes (stderr isn't used for anything by 7-zip)
		#set reasonable sized buffer
		self.filename = filename
		pipe = subprocess.Popen((exe7z, 'l', '-slt', self.filename), stdout=subprocess.PIPE, bufsize=4096)

		self.data, err = pipe.communicate()

		#wait for it to finish, (it should be finished by now)
		#if error code is not zero, raise the errors we saved for later
		if pipe.wait() != 0:
			errors = (line for line in self.data.splitlines() if line.startswith(b'Error:'))
			for error in errors:
				if error.endswith(b'Can not open file as archive'):
					raise NotSupportedArchive(_unicode(error))
				else:
					raise Exception(_unicode(error))

	def __iter__(self):
		errors = []

		#walk through stdout of 7-zip command line-by-line
		#output looks like field = value\r\nfield2=value\r\n\r\nnew record
		#output will be in Bytes, remember to convert to unicode
		isdir = None
		#for line in pipe.stdout:
		for line in self.data.splitlines():
			line = _unicode(line).rstrip('\r\n')
			if line.startswith('Path = '):
				path = line[7:]
			elif line.startswith('Attributes = '):
				atts = line[13:]
				isdir = atts[0] == 'D'
			elif line.startswith('CRC = '):
				crc = line[6:]
				if crc == '':
					crc = None
				else:
					crc = long(crc, base=16)
				errors.append(line)
			elif line == '' and isdir is not None:
				#end of record and not directory
				yield ArchiveItem(isdir, crc, path)

	

openarchive = Archive
