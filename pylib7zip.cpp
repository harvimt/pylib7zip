/*
 * Copyright (c) 2012, Mark Harviston <mark.harviston@gmail.com>
 * This is free software, most forms of redistribution and derivitive works are permitted with the following restrictions.
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

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
			case C7Z_NO_ERROR:
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

	//Type/Object Definitions
	
	// Archive
	typedef struct {
		PyObject_HEAD
		/* Type-specific fields go here. */
		C7ZipArchive *archive_obj;
	} p7z_Archive;

	static PyObject* p7z_arc_close(p7z_Archive* self, PyObject* args);
	static void p7z_arc_del(p7z_Archive *self);

	static PyMethodDef p7z_Archive_Meth[] = {
		{"close", (PyCFunction) p7z_arc_close, METH_VARARGS, "Close the archive"},
		{NULL}  /* Sentinel */
	};

	static long int p7z_arc_Len(p7z_Archive* self);

	static PyObject* p7z_arc_GetItem(p7z_Archive* self, long int index);
	static PyObject* p7z_arc_iter(p7z_Archive* self);

	static PySequenceMethods p7z_arc_asSeq = {
		(lenfunc) p7z_arc_Len,      /* inquiry sq_length;             // __len__ */
		0,                /* binaryfunc sq_concat;          // __add__ */
		0,                /* intargfunc sq_repeat;          // __mul__ */
		(ssizeargfunc) p7z_arc_GetItem,  /* intargfunc sq_item;            // __getitem__ */
		0,                /* intintargfunc sq_slice;        // __getslice__ */
		0,                /* intobjargproc sq_ass_item;     // __setitem__ */
		0,                /* intintobjargproc sq_ass_slice; // __setslice__ */
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
		Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER | Py_TPFLAGS_BASETYPE, /* tp_flags*/ //TODO HAVE_ITER
		"lib7zip Archive Object",  /* tp_doc */
		0,                         /* tp_traverse */
		0,                         /* tp_clear */
		0,                         /* tp_richcompare */
		0,                         /* tp_weaklistoffset */
		(getiterfunc) p7z_arc_iter,/* tp_iter */
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

	//ArchiveIterator
	typedef struct {
		PyObject_HEAD
		p7z_Archive* archive;
		long unsigned int index;
		unsigned int item_count;
	} p7z_ArchiveIter;

	static void p7z_arciter_del(p7z_ArchiveIter *self);
	static PyObject* p7z_arciter_iter(p7z_ArchiveIter *self);
	static PyObject* p7z_arciter_iternext(p7z_ArchiveIter *self);

	static PyTypeObject p7z_ArchiveIter_Type = {
		PyObject_HEAD_INIT(NULL)
		0,                         /* ob_size*/
		"lib7zip.ArchiveIterator", /* tp_name*/
		sizeof(p7z_ArchiveIter),   /* tp_basicsize*/
		0,                         /* tp_itemsize*/
		(destructor)p7z_arciter_del, /* tp_dealloc*/
		0,                         /* tp_print*/
		0,                         /* tp_getattr*/
		0,                         /* tp_setattr*/
		0,                         /* tp_compare*/
		0,                         /* tp_repr*/
		0,                         /* tp_as_number*/
		0,                         /* tp_as_sequence*/
		0,                         /* tp_as_mapping*/
		0,                         /* tp_hash */
		0,                         /* tp_call*/
		0,                         /* tp_str*/
		0,                         /* tp_getattro*/
		0,                         /* tp_setattro*/
		0,                         /* tp_as_buffer*/
		Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER, /*tp_flags*/
		"lib7zip Archive Iterator Object",  /* tp_doc */
		0,                         /* tp_traverse */
		0,                         /* tp_clear */
		0,                         /* tp_richcompare */
		0,                         /* tp_weaklistoffset */
		(getiterfunc) p7z_arciter_iter,    /* tp_iter */
		(getiterfunc) p7z_arciter_iternext,/* tp_iternext */
		0,                         /* tp_methods */
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

	//ArchiveItem
	typedef struct {
		PyObject_HEAD
		C7ZipArchiveItem *archive_item_obj;
	} p7z_ArchiveItem;

	static void p7z_arcitem_del(p7z_ArchiveItem *self);
	static PyObject* p7z_arcitem_isDir(p7z_ArchiveItem *self, void *closure);
	static PyObject* p7z_arcitem_getpath(p7z_ArchiveItem *self, void *closure);
	static PyObject* p7z_arcitem_getsize(p7z_ArchiveItem *self, void *closure);
	static PyObject* p7z_arcitem_isencrypted(p7z_ArchiveItem *self, void *closure);
	static PyObject* p7z_arcitem_getchecksum(p7z_ArchiveItem *self, void *closure);
	static PyObject* p7z_arcitem_getcrc(p7z_ArchiveItem *self, void *closure);
	static PyObject* p7z_arcitem_getindex(p7z_ArchiveItem *self, void *closure);

	static PyGetSetDef p7z_arcitem_GetSet[] = {
		{"isdir",  (getter)p7z_arcitem_isDir, NULL, "Return True if item is a directory and False otherwise.", NULL},
		{"path",   (getter)p7z_arcitem_getpath, NULL, "file path.", NULL},
		{"size",   (getter)p7z_arcitem_getsize, NULL, "file size.", NULL},
		{"isencrypted",(getter)p7z_arcitem_isencrypted, NULL, "Whether the file is encrypted (and requires a password to extract)", NULL},
		{"index",(getter)p7z_arcitem_getindex, NULL, "The index of the item in the archive.", NULL},
		{"checksum",(getter)p7z_arcitem_getchecksum, NULL, "The file's checksum.", NULL},
		{"crc",(getter)p7z_arcitem_getcrc, NULL, "The file's CRC.", NULL},
		{NULL} //Sentinel
	};

	static PyTypeObject p7z_ArchiveItem_Type = {
		PyObject_HEAD_INIT(NULL)
			0,                     /* ob_size*/
		"lib7zip.ArchiveItem",     /* tp_name*/
		sizeof(p7z_ArchiveItem),   /* tp_basicsize*/
		0,                         /* tp_itemsize*/
		(destructor)p7z_arcitem_del, /* tp_dealloc*/
		0,                         /* tp_print*/
		0,                         /* tp_getattr*/
		0,                         /* tp_setattr*/
		0,                         /* tp_compare*/
		0,                         /* tp_repr*/
		0,                         /* tp_as_number*/
		0,                         /* tp_as_sequence*/
		0,                         /* tp_as_mapping*/
		0,                         /* tp_hash */
		0,                         /* tp_call*/
		0,                         /* tp_str*/
		0,                         /* tp_getattro*/
		0,                         /* tp_setattro*/
		0,                         /* tp_as_buffer*/
		Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
		"lib7zip ArchiveItem Object",  /* tp_doc */
		0,                         /* tp_traverse */
		0,                         /* tp_clear */
		0,                         /* tp_richcompare */
		0,                         /* tp_weaklistoffset */
		0,                         /* tp_iter */
		0,                         /* tp_iternext */
		0,                         /* tp_methods */
		0,                         /* tp_members */
		p7z_arcitem_GetSet,        /* tp_getset */
		0,                         /* tp_base */
		0,                         /* tp_dict */
		0,                         /* tp_descr_get */
		0,                         /* tp_descr_set */
		0,                         /* tp_dictoffset */
		0,                         /* tp_init */
		PyType_GenericAlloc,       /* tp_alloc */
		PyType_GenericNew,         /* tp_new */
	};

	//Initialize Module

	PyObject* clearmem(void);
	PyObject* openarchive(PyObject* self, PyObject* args);

	static PyMethodDef Lib7zMethods[] = {
		{"openarchive",  openarchive, METH_VARARGS,
			"Open the archive, return an Archive object."},
		{"clearmem",  (PyCFunction) clearmem, METH_NOARGS,
			"Reinitialize the Library to clear it's memory."},
		{NULL, NULL, 0, NULL}/* Sentinel */
	};

	PyMODINIT_FUNC initlib7zip(void) {
		PyObject *m;

		//Create Types/Objects
		if (PyType_Ready(&p7z_Archive_Type) < 0) return;
		if (PyType_Ready(&p7z_ArchiveItem_Type) < 0) return;

		//Initialize Module
		m = Py_InitModule("lib7zip", Lib7zMethods);
		if (m == NULL) return;

		//INCREF/AddObject Types/Objects

		Py_INCREF(&p7z_Archive_Type);
		PyModule_AddObject(m, "Archive", (PyObject*)&p7z_Archive_Type);

		Py_INCREF(&p7z_ArchiveIter_Type);
		//PyModule_AddObject(m, "ArchiveIterator", (PyObject*)&p7z_ArchiveIter_Type); //FIXME, this causes segfaults, but I don't know why

		Py_INCREF(&p7z_ArchiveItem_Type);
		PyModule_AddObject(m, "ArchiveItem", (PyObject*)&p7z_ArchiveItem_Type);

		//Create Exceptions
		NEW_EXCEPTION(UnknownError, "UnknownError");
		NEW_EXCEPTION(NotInitialized, "NotInitialized");
		NEW_EXCEPTION(NeedsPassword, "NeedsPassword");
		NEW_EXCEPTION(NotSupportedArchive, "NotSupportedArchive");

		//lib7zip Initialize
		lib.Initialize();
	}

	PyObject* openarchive(PyObject* self, PyObject* args) {
		char* filename;

		if (!PyArg_ParseTuple(args, "s", &filename)){
			return NULL;
		}

		FILE* file = fopen(filename, "rb");

		if(!file){
			PyErr_SetFromErrnoWithFilename(PyExc_IOError, filename);
			return NULL;
		}

		C7ZipInStreamFWrapper instream(file, L"7z");

		C7ZipArchive* archive = NULL;
		CHECK_CALL(lib.OpenArchive(&instream, &archive), "Failed to open archive");

		p7z_Archive *arc_obj = (p7z_Archive*) p7z_Archive_Type.tp_new(&p7z_Archive_Type, NULL, NULL);
		Py_INCREF(arc_obj);

		arc_obj->archive_obj = archive;

		return (PyObject*) arc_obj;
	}

	static void p7z_arc_del(p7z_Archive *self) {
		delete self->archive_obj;
		self->ob_type->tp_free((PyObject*)self);
	}

	static PyObject* p7z_arc_close(p7z_Archive* self, PyObject* args) {
		self->archive_obj->Close();
		Py_RETURN_NONE;
	}

	static int long p7z_arc_Len(p7z_Archive* self) {
		unsigned int item_count;
		CHECK_CALL_R(self->archive_obj->GetItemCount(&item_count), "GetItemCount failed", -1);
		return item_count;
	}

	static PyObject*
	p7z_arc_GetItem(p7z_Archive* self, long int index) {
		unsigned int item_count;
		CHECK_CALL(self->archive_obj->GetItemCount(&item_count), "GetItemCount failed");

		if(index >= item_count){
			PyErr_SetString(PyExc_IndexError, "Index out of range");
		}

		C7ZipArchiveItem* item;
		CHECK_CALL(self->archive_obj->GetItemInfo(index, &item), "GetItemInfo failed");
		if(item == NULL){
			PyErr_SetString(UnknownError, "NULL Pointer");
		}

		p7z_ArchiveItem* _item = (p7z_ArchiveItem*) p7z_ArchiveItem_Type.tp_new(&p7z_ArchiveItem_Type, NULL, NULL);
		Py_INCREF(_item);

		_item->archive_item_obj = item;

		return (PyObject*) _item;
	}

	static void p7z_arcitem_del(p7z_ArchiveItem *self) {
		//delete self->archive_item_obj; //deleteing an Archive deletes all it's Items
		self->ob_type->tp_free((PyObject*)self);
	}

	static PyObject*
	p7z_arcitem_isDir(p7z_ArchiveItem *self, void *closure) {
		return Py_BuildValue("b", self->archive_item_obj->IsDir());
	}

	static PyObject*
	p7z_arcitem_getpath(p7z_ArchiveItem *self, void *closure) {
		return Py_BuildValue("u", self->archive_item_obj->GetFullPath().c_str());
	}

	static PyObject*
	p7z_arcitem_getsize(p7z_ArchiveItem *self, void *closure) {
		return Py_BuildValue("K", self->archive_item_obj->GetSize());
	}

	static PyObject*
	p7z_arcitem_isencrypted(p7z_ArchiveItem *self, void *closure) {
		return Py_BuildValue("b", self->archive_item_obj->IsEncrypted());
	}

	static PyObject*
	p7z_arcitem_getindex(p7z_ArchiveItem *self, void *closure) {
		return Py_BuildValue("k", self->archive_item_obj->GetArchiveIndex());
	}

	#define GET_UINT64_PROP(funcname, propid) \
	static PyObject* \
	p7z_arcitem_##funcname(p7z_ArchiveItem *self, void *closure){\
		unsigned __int64 val; \
		if(!self->archive_item_obj->GetUInt64Property(propid, val)){ \
			Py_RETURN_NONE; \
		}else{ \
			return Py_BuildValue("K", val); \
		}\
	}

	GET_UINT64_PROP(getchecksum, kpidChecksum);

	GET_UINT64_PROP(getcrc, kpidCRC);

	//Iterator
	static void p7z_arciter_del(p7z_ArchiveIter *self) {
		Py_XDECREF(self->archive);
		self->ob_type->tp_free((PyObject*)self);
	}

	static PyObject* p7z_arciter_iter(p7z_ArchiveIter *self) {
		Py_INCREF(self);
		return (PyObject*)self;
	}

	static PyObject* p7z_arciter_iternext(p7z_ArchiveIter *self) {

		C7ZipArchiveItem* item;

		if (self->index >= self->item_count){
			PyErr_SetNone(PyExc_StopIteration);
			return NULL;
		}

		CHECK_CALL(self->archive->archive_obj->GetItemInfo(self->index, &item), "GetItemInfo failed");
		if(item == NULL){
			PyErr_SetString(UnknownError, "NULL Pointer");
		}

		p7z_ArchiveItem* _item = (p7z_ArchiveItem*) p7z_ArchiveItem_Type.tp_new(&p7z_ArchiveItem_Type, NULL, NULL);
		Py_INCREF(_item);

		_item->archive_item_obj = item;

		self->index += 1;

		return (PyObject*) _item;
	}

	static PyObject* p7z_arc_iter(p7z_Archive *self) {
		p7z_ArchiveIter * iter = (p7z_ArchiveIter*) p7z_ArchiveIter_Type.tp_new(&p7z_ArchiveIter_Type, NULL, NULL);
		Py_INCREF(iter);

		Py_INCREF(self);
		iter->archive = self;
		iter->index = 0;

		CHECK_CALL(self->archive_obj->GetItemCount(&(iter->item_count)), "Failed to get item count.");

		return (PyObject*) iter;
	}

	PyObject* clearmem() {
		lib.Deinitialize();
		CHECK_CALL(lib.Initialize(), "Failed to Re-Initialize 7zip Library");
		Py_RETURN_NONE;
	}

}
