#include <python2.7/Python.h>
#include "clib7zip.h"

extern "C" {

static PyObject *
p7z_openarchive(PyObject *self, PyObject *args);

static PyMethodDef P7ZMethods[] = {
	{"openarchive", p7z_openarchive, METH_VARARGS, "Open a 7-Zip Archive"}
};

PyMODINIT_FUNC
initpy7z(void){
	(void) Py_InitModule("pylib7z", P7ZMethods);


}

static PyObject *
p7z_openarchive(PyObject *self, PyObject *args)
{
	(void) self;
	(void) args;
		
	//TODO
	return NULL;
}

}
