from .comtypes import IID_IUnknown
from .py7ziptypes import IID_IInStream

from .wintypes import guidp2uuid, S_OK
from . import log, ffi, wintypes

GUIDS = {
	IID_IInStream: 'IInStream',
}

class FileInStream():
	def __init__(self, filename):
		self.filelike = open(filename, 'rb')
		self.ref = 1

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

		if uu == IID_IUnknown:
			out_ref[0] = me
			return S_OK
		elif uu in self.instances:
			log.debug('found guid')
			out_ref[0] = self.instances[uu]
			return S_OK
		else:
			#log.debug(uu)
			log.warn('Unknown GUID {!r}'.format(uu))
			
			out_ref[0] = ffi.NULL
			return wintypes.E_NOINTERFACE
	
	def AddRef(self, me):
		log.debug('stream AddRef')
		self.ref += 1
		return self.ref
	
	def Release(self, me):
		log.debug('stream Release')
		self.ref -= 1
		return self.ref
	
	def Read(self, me, data, size, processed_size):
		log.debug('Read size={}'.format(size))
		buf = self.filelike.read(size)
		psize = len(buf)

		if processed_size != ffi.NULL:
			processed_size[0] = psize
		
		data[0:psize] = buf[0:psize]
		log.debug('processed size: {}'.format(psize))

		return S_OK
	
	def Seek(self, me, offset, origin, newposition):
		log.debug('Seek offset={}; origin={}'.format(offset, origin))
		newpos = self.filelike.seek(offset, origin)
		if newposition != ffi.NULL:
			newposition[0] = newpos
		log.debug('new position: {}'.format(newpos))
		return S_OK