from .comtypes import IID_IUnknown
from .py7ziptypes import IID_ICryptoGetTextPassword, IID_IArchiveOpenCallback, IID_IArchiveOpenVolumeCallback, IID_IArchiveOpenSetSubArchiveName

from .wintypes import guidp2uuid, S_OK
from . import log, ffi, wintypes

#import logging
#log = logging.getLogger('lib7zip')

GUIDS = {
	IID_ICryptoGetTextPassword: 'ICryptoGetTextPassword',
	IID_IArchiveOpenCallback: 'IArchiveOpenCallback',
	IID_IArchiveOpenVolumeCallback: 'IArchiveOpenVolumeCallback',
	IID_IArchiveOpenSetSubArchiveName: 'IArchiveOpenSetSubArchiveName',
}

class ArchiveOpenCallback:
	def __init__(self, password='', stream=None):
		self.password = ffi.new('wchar_t[]', password)
		self.ref = 1
		self.stream = stream
		self.subarchive_name = None
		
		self.vtables = []
		self.instances = {}
		self.methods = {}
		
		for iid, interface in GUIDS.items():
			vtable = ffi.new('_' + interface + '_vtable*')
			instance = ffi.new(interface + '*')
			instance.vtable = vtable
			
			for name, method_type in ffi.typeof(vtable).item.fields:
				try:
					method = self.methods[name]
				except KeyError:
					ctype = ffi.typeof(getattr(vtable, name))
					self.methods[name] = method = ffi.callback(ctype, getattr(self, name))
				
				setattr(vtable, name, method)
			self.vtables.append(vtable)
			self.instances[iid] = instance

	def QueryInterface(self, me, iid, out_ref):
		uu = guidp2uuid(iid)
		log.debug('Callback Interface Queried %r, %r' % (self, uu) )
		self.ref += 1
		if uu == IID_IUnknown:
			out_ref[0] = me
			return S_OK
		elif uu in self.instances:
			log.debug('found guid')
			out_ref[0] = self.instances[uu]
			return S_OK
		else:
			log.warn('Unknown GUID {!r}'.format(uu))
			
			out_ref[0] = ffi.NULL
			return wintypes.E_NOINTERFACE
		
	def AddRef(self, me):
		log.debug('callback AddRef')
		self.ref += 1
		log.debug('refcount: {}'.format(self.ref))
		return self.ref
	
	def Release(self, me):
		log.debug('callback Release')
		self.ref -= 1
		log.debug('refcount: {}'.format(self.ref))
		return self.ref
	
	def SetTotal(self, me, files, bytes):
		log.debug('on_set_total')
		return S_OK
	
	def SetCompleted(self, me, files, bytes):
		log.debug('on_set_completed')
		return S_OK

	def CryptoGetTextPassword(self, me, password):
		log.debug('GetPassword')
		password[0] = self.password
		return S_OK
	
	def GetProperty(self, me, propID, value):
		log.debug('GetProperty propID={}'.format(propID))
		value.vt = wintypes.VT_EMPTY
		return S_OK

	def GetStream(self, me, name, inStream):
		log.debug('GetStream name={}'.format(name))
		inStream[0] = self.stream.stream
		return S_OK
	
	def SetSubArchiveName(self, me, name):
		name = ffi.string(name)
		log.debug('SetSubArchiveName: {}'.format(name))
		self.subarchive_name = name
		return S_OK