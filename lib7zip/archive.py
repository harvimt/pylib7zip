from functools import partial

from . import ffi, dll7z, max_sig_size, formats, log
from . import py7ziptypes

from .winhelpers import uuid2guidp, get_prop_val, RNOK

from .open_callback import ArchiveOpenCallback
from .extract_callback import ArchiveExtractToDirectoryCallback, ArchiveExtractToStreamCallback
from .stream import FileInStream

class Archive:
	def __init__(self, filename, forcetype=None, password=None):
		self.tmp_archive = ffi.new('void**')
		iid = uuid2guidp(py7ziptypes.IID_IInArchive)

		self.stream = FileInStream(filename)
		stream_inst = self.stream.instances[py7ziptypes.IID_IInStream]
		
		if forcetype is not None:
			format = formats[forcetype]
		else:
			format = self._guess_format()
			
		classid = uuid2guidp(format.classid)
		
		RNOK(dll7z.CreateObject(classid, iid, self.tmp_archive))
		assert self.tmp_archive[0] != ffi.NULL
		self.archive = archive = ffi.cast('IInArchive*', self.tmp_archive[0])
		
		callback = ArchiveOpenCallback(password=password)
		callback_inst = callback.instances[py7ziptypes.IID_IArchiveOpenCallback]
		
		maxCheckStartPosition = ffi.new('uint64_t*', 1 << 22)
		RNOK(archive.vtable.Open(archive, stream_inst, maxCheckStartPosition, callback_inst))
		self.itm_prop_fn = partial(archive.vtable.GetProperty, archive)
	
	def _guess_format(self):
		file = self.stream.filelike
		sigcmp = file.read(max_sig_size)
		for name, format in formats.items():
			if format.start_signature and sigcmp.startswith(format.start_signature):
				log.debug('guessed: %s' % name)
				file.seek(0)
				return format

		assert False

	def __enter__(self, *args, **kwargs):
		return self
	
	def __exit__(self, *args, **kwargs):
		self.close()
	
	def __del__(self):
		self.close()
	
	def close(self):
		RNOK(self.archive.vtable.Close(self.archive))
	
	def __len__(self):
		num_items = ffi.new('uint32_t*')
		RNOK(self.archive.vtable.GetNumberOfItems(self.archive, num_items))
		return int(num_items[0])
	
	def __getitem__(self, index):
		if index > len(self):
			raise IndexError()
		return ArchiveItem(self, index)
	
	def __iter__(self):
		for i in range(len(self)):
			yield self[i]
			#isdir = get_bool_prop(i, py7ziptypes.kpidIsDir, self.itm_prop_fn)
			#path = get_string_prop(i, py7ziptypes.kpidPath, self.itm_prop_fn)
			#crc = get_hex_prop(i, py7ziptypes.kpidCRC, self.itm_prop_fn)
			#yield isdir, path, crc
		
	def __getattr__(self, attr):
		pass
	
	def extract(self, directory=''):
		'''
			IInArchive::Extract:
			indices must be sorted
			numItems = 0xFFFFFFFF means "all files"
			testMode != 0 means "test files without writing to outStream"
		'''
		callback = ArchiveExtractToDirectoryCallback(self, directory)
		callback_inst = callback.instances[py7ziptypes.IID_IArchiveExtractCallback]
		#indices = ffi.new('uint32_t[]', [])
		RNOK(self.archive.vtable.Extract(self.archive, ffi.NULL, 0xFFFFFFFF, 0, callback_inst))
		callback.flush_and_close_streams()
		#callback.out_file.filelike.flush()
		#callback.out_file.filelike.close()

class ArchiveItem():
	def __init__(self, archive, index):
		self.archive = archive
		self.index = index
		
	def extract(self, file):
		callback = ArchiveExtractToStreamCallback(file, self.index)
		callback_inst = callback.instances[py7ziptypes.IID_IArchiveExtractCallback]
		#indices = ffi.new('const uint32_t indices[]', [self.index])
		
		#indices_p = C.calloc(1, ffi.sizeof('uint32_t'))
		#indices = ffi.cast('uint32_t*', indices_p)
		#indices[0] = self.index
		
		log.debug('got here!')
		RNOK(self.archive.archive.vtable.Extract(self.archive.archive, ffi.NULL, 0xFFFFFFFF, 0, callback_inst))
		log.debug('done')
		#C.free(indices_p)

	def __getattr__(self, attr):
		propid = getattr(py7ziptypes.ArchiveProps, attr)
		return get_prop_val(partial(self.archive.itm_prop_fn, self.index, propid))