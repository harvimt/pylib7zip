"""
Helper functions for dealing with windows types defined in wintypes like PROPVARIANT, GUID*, and HRESULT
"""

import uuid
from . import ffi, C, free_propvariant, log
from .wintypes import *
#from bitstring import BitArray
#import warnings

def guidp2uuid(guid):
	"""GUID* -> uuid.UUID"""
	#if guid == ffi.NULL:
	#	return None
	return uuid.UUID(bytes_le=bytes(guid[0]))

def uuid2guidp(uu):
	"""uuid.UUID -> GUID*"""
	return ffi.new('GUID*', uu.bytes_le)

class HRESULTException(Exception): pass

def RNOK(code):
	""" raise error if not S_OK """
	# TODO raise different Exception based on result
	if code == HRESULT.S_OK.value: return
	#parse HRESULT
	
	'''
	barr = BitArray(uint=code, length=32)

	# first 2 bits are status
	SUCCESS = '0b00'
	INFO = '0b01'
	WARN = '0b10'
	ERROR = '0b11'
	status = barr[0:2]

	#next says whether this is user-defined or not
	is_cust = barr[2]
	# reserved bit (should always be 0?)
	reserved = barr[3]
	log.debug('is_cust=%r; reserved=%r', is_cust, reserved)
	# what errored e.g. the "facility"
	facility = barr[4:12].uint
	# finally, the code
	h_code = barr[16:].uint

	if code == HRESULT.S_FALSE:
		raise HRESULTException('S_FALSE')
	elif status == SUCCESS:
		log.info('SUCCESS, but not S_OK, %d/%04x', facility, h_code)
	elif status == INFO:
		log.info('INFO %d/%04x', facility, h_code)
	elif status == WARN:
		log.warn('WARNING, %d/%04x' % (facility, h_code))
	elif status == ERROR:
		try:
			hresult = HRESULT(code)
			raise HRESULTException(hresult.name + ': ' + hresult.desc)
		except ValueError:
			raise HRESULTException('HRESULT, %d/04x', facility, h_code)
	'''

	try:
		hresult = HRESULT(code)
		raise HRESULTException(hresult.name + ': ' + hresult.desc)
	except ValueError:
		raise HRESULTException('HRESULT, %08x', code)

def dealloc_propvariant(pvar):
	log.debug('deallocing propvariant')
	if pvar == ffi.NULL:
		log.debug('pvar == NULL')
		return
	log.debug('...')
	free_propvariant(pvar)
	log.debug('...')
	C.free(pvar)
	pvar = ffi.NULL
	log.debug('...')
	log.debug('dealloced propvariant')

def alloc_propvariant():
	return ffi.gc(C.calloc(1, ffi.sizeof('PROPVARIANT')), dealloc_propvariant)
	#return ffi.new('PROPVARIANT*')
	
def get_prop_val(fn, forcetype=None, checktype=None):
	"""
	fn should have the signature:
	HRESULT fn(PROPVARIANT*);
	"""
	ptr = alloc_propvariant()
	RNOK(fn(ptr))
	pvar = ffi.cast('PROPVARIANT*', ptr)
	vt = forcetype or pvar.vt
	if pvar.vt in (VARTYPE.VT_EMPTY, VARTYPE.VT_NULL):
		# always check for null, pvar.vt is not a bug
		return None
		
	if checktype:
		if checktype == True:
			checktype = forcetype
		assert pvar.vt == checktype

	if vt in (VARTYPE.VT_UI4, VARTYPE.VT_UINT):
		return int(pvar.ulVal)
	elif vt == VARTYPE.VT_UI8:
		return int(pvar.uhVal)
	elif vt == VARTYPE.VT_BOOL:
		return int(pvar.bVal) != 0
	elif vt == VARTYPE.VT_CLSID:
		return guidp2uu(pvar.puuid)
	elif vt == VARTYPE.VT_BSTR:
		return ffi.string(pvar.bstrVal)
	else:
		raise TypeError("type code %d not supported" % vt)
