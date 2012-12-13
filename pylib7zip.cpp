#include <cstdlib>

extern "C" {

	#include "python2.7/Python.h"

	static PyObject *
		p7z_system(PyObject *self, PyObject *args)
		{
			const char *command;
			int sts;

			if (!PyArg_ParseTuple(args, "s", &command))
				return NULL;
			sts = system(command);
			return Py_BuildValue("i", sts);
		}

	static PyMethodDef Lib7zMethods[] = {
		{"system",  p7z_system, METH_VARARGS,
			"Execute a shell command."},
		{NULL, NULL, 0, NULL}        /* Sentinel */
	};

	PyMODINIT_FUNC
		initlib7zip(void)
		{
			PyObject *m;

			m = Py_InitModule("lib7zip", Lib7zMethods);
			if (m == NULL) return;

		}

}
