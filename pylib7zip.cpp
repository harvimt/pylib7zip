#include <cstdlib>
#include <lib7zip.h>
#include "cpplib7z.h"

extern "C" {

	#include "python2.7/Python.h"
	#include <python2.7/structmember.h>

	static C7ZipLibrary lib; // global variable

	//Error Handling
	static PyObject* UnknownError;
	static PyObject* NotInitialized;
	static PyObject* NeedsPassword;
	static PyObject* NotSupportedArchive;

	inline static PyObject* errCodeToException(lib7zip::ErrorCodeEnum code){
		using namespace lib7zip;
		switch(code){
			case NOT_INITIALIZE:
				return NotInitialized;
				break;
			case NEED_PASSWORD:
				return NeedsPassword;
				break;
			case NOT_SUPPORTED_ARCHIVE:
				 return NotSupportedArchive;
				 break;
			case NO_ERROR:
			case UNKNOWN_ERROR:
			default:
				return UnknownError;
				break;
		}
	}

	#define MODULE_NAME "lib7zip"

	#define CHECK_CALL(call, err) CHECK_CALL_R(call, err, NULL);
	#define CHECK_CALL_R(call, err, ret) if(!call){ PyErr_SetString(errCodeToException(lib.GetLastError()), err); return ret; }

	#define NEW_EXCEPTION(PTR, NAME) PTR = PyErr_NewException(MODULE_NAME "." NAME, NULL, NULL);\
		Py_INCREF(PTR); PyModule_AddObject(m, NAME, PTR);

	//Method Definitions
	#define method_def(name) static PyObject * name(PyObject *self, PyObject *args)

	method_def(openarchive);
	method_def(p7z_arc_close);

	//Type/Object Definitions
	
	// Archive
	typedef struct {
		PyObject_HEAD
		/* Type-specific fields go here. */
		C7ZipArchive *archive_obj;
	} p7z_Archive;

	static void p7z_arc_del(p7z_Archive *self);
	static PyObject* p7z_arc_getExt(p7z_Archive* self, void* closure);

	static PyMethodDef p7z_Archive_Meth[] = {
		{"close", p7z_arc_close, METH_VARARGS, "Close the archive"},
		{NULL}  /* Sentinel */
	};

	/*
	static PyGetSetDef p7z_Archive_GetSet[] = {
		{"extension",
			(getter)p7z_arc_getExt, NULL,
			"File Name Extension",
			NULL},
		{NULL} //Sentinel
	};
	*/

	static long int p7z_arc_Len(PyObject* self);

	static PyObject* p7z_arc_GetItem(PyObject* self, long int index);

	static PySequenceMethods p7z_arc_asSeq = {
		p7z_arc_Len,      /* inquiry sq_length;             // __len__ */
		0,   /* binaryfunc sq_concat;          // __add__ */
		0,    /* intargfunc sq_repeat;          // __mul__ */
		p7z_arc_GetItem,   /* intargfunc sq_item;            // __getitem__ */
		0,  /* intintargfunc sq_slice;        // __getslice__ */
		0,   /* intobjargproc sq_ass_item;     // __setitem__ */
		0,  /* intintobjargproc sq_ass_slice; // __setslice__ */
	};

	static PyTypeObject p7z_Archive_Type = {
		PyObject_HEAD_INIT(NULL)
		0,                         /* ob_size*/
		"lib7zip.Archive",         /* tp_name*/
		sizeof(p7z_Archive),       /* tp_basicsize*/
		0,                         /* tp_itemsize*/
		(destructor)p7z_arc_del,   /* tp_dealloc*/
		0,                         /* tp_print*/
		0,                         /* tp_getattr*/
		0,                         /* tp_setattr*/
		0,                         /* tp_compare*/
		0,                         /* tp_repr*/
		0,                         /* tp_as_number*/
		&p7z_arc_asSeq,            /* tp_as_sequence*/
		0,                         /* tp_as_mapping*/
		0,                         /* tp_hash */
		0,                         /* tp_call*/
		0,                         /* tp_str*/
		0,                         /* tp_getattro*/
		0,                         /* tp_setattro*/
		0,                         /* tp_as_buffer*/
		Py_TPFLAGS_DEFAULT,        /* tp_flags*/ //TODO HAVE_ITER
		"lib7zip Archive Object",  /* tp_doc */
		0,                         /* tp_traverse */
		0,                         /* tp_clear */
		0,                         /* tp_richcompare */
		0,                         /* tp_weaklistoffset */
		0,                         /* tp_iter */
		0,                         /* tp_iternext */
		p7z_Archive_Meth,          /* tp_methods */
		0,                         /* tp_members */
		0,                         /* tp_getset */
		0,                         /* tp_base */
		0,                         /* tp_dict */
		0,                         /* tp_descr_get */
		0,                         /* tp_descr_set */
		0,                         /* tp_dictoffset */
		0,                         /* tp_init */
		PyType_GenericAlloc,       /* tp_alloc */
		PyType_GenericNew,         /* tp_new */
		};

#if false
	//ArchiveItem
	typedef struct {
		PyObject_HEAD
		C7ZipArchiveItem *archive_item;
	} p7z_ArchiveItem;

	static PyTypeObject p7z_ArchiveItem_Type = {
		PyObject_HEAD_INIT(NULL)
			0,                     /*ob_size*/
		"lib7zip.Archive",         /*tp_name*/
		sizeof(p7z_Archive),      /*tp_basicsize*/
		0,                         /*tp_itemsize*/
		(destructor)p7z_arc_del,               /*tp_dealloc*/
		0,                         /*tp_print*/
		0,                         /*tp_getattr*/
		0,                         /*tp_setattr*/
		0,                         /*tp_compare*/
		0,                         /*tp_repr*/
		0,                         /*tp_as_number*/
		0,                         /*tp_as_sequence*/
		0,                         /*tp_as_mapping*/
		0,                         /*tp_hash */
		0,                         /*tp_call*/
		0,                         /*tp_str*/
		0,                         /*tp_getattro*/
		0,                         /*tp_setattro*/
		0,                         /*tp_as_buffer*/
		Py_TPFLAGS_DEFAULT,        /*tp_flags*/
		"lib7zip Archive Object"  /* tp_doc */
	};
#endif

	//Initialize Module

	static PyMethodDef Lib7zMethods[] = {
		{"openarchive",  openarchive, METH_VARARGS,
			"Open the archive, return an Archive object."},
		{NULL, NULL, 0, NULL}        /* Sentinel */
	};

	PyMODINIT_FUNC
		initlib7zip(void)
		{
			PyObject *m;

			//Create Types/Objects
			
			if (PyType_Ready(&p7z_Archive_Type) < 0)
				return;

			//Initialize Module
			m = Py_InitModule("lib7zip", Lib7zMethods);
			if (m == NULL) return;

			//INCREF/AddObject Types/Objects

			Py_INCREF(&p7z_Archive_Type);
			PyModule_AddObject(m, "Archive", (PyObject*)&p7z_Archive_Type);

			//Create Exceptions
			NEW_EXCEPTION(UnknownError, "UnknownError");
			NEW_EXCEPTION(NotInitialized, "NotInitialized");
			NEW_EXCEPTION(NeedsPassword, "NeedsPassword");
			NEW_EXCEPTION(NotSupportedArchive, "NotSupportedArchive");

			//lib7zip Initialize
			lib.Initialize();
		}

	method_def(openarchive) {
		char* filename;

		if (!PyArg_ParseTuple(args, "s", &filename)){
			return NULL;
		}

		FILE* file = fopen(filename, "rb");

		if(!file){
			PyErr_SetString(PyExc_IOError, "Failed to open file");
			return NULL;
		}

		C7ZipInStreamFWrapper instream(file, L"7z");

		C7ZipArchive* archive = NULL;
		CHECK_CALL(lib.OpenArchive(&instream, &archive), "Failed to open archive");

		p7z_Archive *arc_obj = (p7z_Archive*) p7z_Archive_Type.tp_new(&p7z_Archive_Type, NULL, NULL);
		Py_INCREF(arc_obj);

		return (PyObject*) arc_obj;
	}

	static void p7z_arc_del(p7z_Archive *self){
		delete ((p7z_Archive*)self)->archive_obj;
		self->ob_type->tp_free((PyObject*)self);
	}

	method_def(p7z_arc_close){
		Py_RETURN_NONE;
	}

	//static PyObject* p7z_arc_getExt(p7z_Archive* self, void* closure){
		//const wchar_t *  = self->archive_obj->GetExt().c_str();
	//}

	static int long p7z_arc_Len(PyObject* self)
	{
		p7z_Archive* _self = (p7z_Archive*) self;
		unsigned int item_count;
		CHECK_CALL_R(_self->archive_obj->GetItemCount(&item_count), "GetItemCount failed", -1);
		return item_count;
	}

	static PyObject*
	p7z_arc_GetItem(PyObject* self, long int index){
		return Py_BuildValue("i", index);

		//Py_RETURN_NONE; // TODO
	}

}
