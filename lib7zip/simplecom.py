#!/usr/bin/python
"""
Simple COM, using DRY principles, but w/o too much meta
"""
import logging
from . import ffi, guidp2uuid
from . import wintypes
from .comtypes import IID_IUnknown
from .wintypes import HRESULT
log = logging.getLogger(__name__)

"""
import functools

def createCOMStructs(classname : str, ctypes : str):
	return '''
	typedef struct {{
		{ctypes}
	}} _{classname}_vtable;
	
	typedef struct {{
		_{classname}_vtable* vtable;
	}} {classname};
	'''.format(classname, ctypes)
"""

class IUnknownImpl:
	def __init__(self):
		self.ref = 1
		self.vtables = []
		self.instances = {}
		self.methods = {}
		
		for iid, interface in self.GUIDS.items():
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
		#log.debug('Callback Interface Queried %r' % (uu) )
		self.ref += 1
		if uu == IID_IUnknown:
			log.debug('IIUnknown Queried')
			out_ref[0] = me
			return HRESULT.S_OK.value
		elif uu in self.instances:
			log.debug('found guid: %s' % self.GUIDS[uu])
			out_ref[0] = self.instances[uu]
			#out_ref[0] = me
			return HRESULT.S_OK.value
		else:
			log.warn('Unknown GUID {!r} on {}'.format(uu, type(self).__name__))
			
			out_ref[0] = ffi.NULL
			return HRESULT.E_NOINTERFACE.value
		
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
	
	def __del__(self):
		log.debug('__del__')