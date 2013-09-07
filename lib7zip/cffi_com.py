from uuid import UUID
from copy import copy as shallowcopy
from functools import update_wrapper
from collections import OrderedDict
import inspect


from . import ffi

"""
Implement Basic COM Types

There's so much meta going on here.
"""

class GUID(UUID):
	def toGUID(self):
		guid = ffi.new('GUID*')
		data = ffi.cast('uint8_t[16]', guid)
		data[0:16] = self.bytes_le
		return guid
	
	@staticmethod
	def fromGUID(guid):
		data = ffi.cast('uint8_t[16]', guid)
		return UUID(bytes_le=bytes(data[0:16]))

class ArgWrapper:
	def __init__(self, ctype, converter=None):
		self.value = ctype
		self.converter = converter

class in_(ArgWrapper):
	""" COM in argument """

class out_(ArgWrapper):
	"""COM out argument"""

class MethodWrapper:
	def __init__(self, fn):
		self.fn = fn

	def __call__(self, obj, *args, **kwargs):
		reg_method = type(obj).registry[self.fn.__name__]
		dllfn = getattr(obj.pointer.vtable, reg_method.name)
		dllfn(obj.pointer, *args, **kwargs)
		return self.fn(*args, **kwargs)

def method(fn):
	wrapper = MethodWrapper(fn)
	update_wrapper(wrapper, fn)
	return wrapper

RegisteredMethod = namedtuple('RegisteredMethod', ('name', 'ctype', 'in_args', 'out_args'))
class COMClass(type):
	def __prepare__(self, name, bases):
		return OrderedDict()

	def __new__(self, classname, bases, members):
		assert len(bases) <= 1

		newclass = super().__new__(classname, bases, members.items())

		if bases:
			registry = shallowcopy(bases[0].registry)
		else:
			registry = OrderedDict()
		
		for name, member in members.items():
			if isinstance(member, MethodWrapper):
				sig = inspect.signature(member)
				ctype = "{result}(*{name})({args});".format(
					result=sig.return_annotation,
					name=name,
					args=', '.join(p.annotation.ctype for p in sig.parameters),
				)
				in_args  = tuple(a.name for a in sig.parameters if isinstance(a, in_))
				out_args = tuple(a.name for a in sig.parameters if isinstance(a, out_))
				
				registry[name] = RegisteredMethod(name, ctype, in_args, out_args)

		newclass.registry = registry
		
		#I'd use .format but there
		ffi.cdef('''
		typedef struct {{
			{ctypes}
		}} _{classname}_vtable;
		
		typedef struct {{
			_{classname}_vtable* vtable;
		}} {classname};
		'''.format(
			classname = classname,
			ctypes = '\n'.join(ma.ctype for ma in registry),
		))

		return newclass


class IUnknown(metaclass=COMClass):
	__iid__ = UUID('{}')
	
	def __init__(self):
		self.pointer = ffi.new(type(self).__name__ + '*')

	@method
	def QueryInterface(
		self,
		iid:    'GUID*',
		result: 'void**'
	) -> 'HRESULT':
		pass