#!/usr/bin/python
"""
Simple COM, using DRY principles but no OOP
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


def bindMethod(self : 'void**', method : str):
	fn = getattr(self[0].vtable, method)
	return functools.partial(fn, self[0])

