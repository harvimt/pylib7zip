
from .py7ziptypes import IID_IInStream, IID_ISequentialInStream,  IID_IOutStream, IID_ISequentialOutStream

from .wintypes import S_OK
from .winhelpers import guidp2uuid
from . import log, ffi, wintypes

from .simplecom import IUnknownImpl

class FileInStream(IUnknownImpl):
	"""
		Implementation of IInStream and ISequentialInStream on top of python file-like objects
		
		Creator responsible for closing the file-like objects.
	"""
	GUIDS = {
		IID_IInStream: 'IInStream',
		IID_ISequentialInStream: 'ISequentialInStream',
	}
	
	def __init__(self, file):
		if isinstance(file, str):
			self.filelike = open(file, 'rb')
		else:
			self.filelike = file
		super().__init__()
	
	def Read(self, me, data, size, processed_size):
		#log.debug('Read size={}'.format(size))
		buf = self.filelike.read(size)
		psize = len(buf)

		if processed_size != ffi.NULL:
			processed_size[0] = psize
		
		data[0:psize] = buf[0:psize]
		#log.debug('processed size: {}'.format(psize))

		return S_OK
	
	def Seek(self, me, offset, origin, newposition):
		#log.debug('Seek offset={}; origin={}'.format(offset, origin))
		newpos = self.filelike.seek(offset, origin)
		if newposition != ffi.NULL:
			newposition[0] = newpos
		#log.debug('new position: {}'.format(newpos))
		return S_OK


class FileOutStream(IUnknownImpl):
	"""
		Implementation of IOutStream and ISequentialOutStream on top of Python file-like objects. 
		
		Creator is responsible for flushing/closing the file-like object
	"""
	GUIDS = {
		IID_IOutStream: 'IOutStream',
		IID_ISequentialOutStream: 'ISequentialOutStream',
	}
	
	def __init__(self, file):
		if isinstance(file, str):
			self.filelike = open(file, 'wb')
		else:
			self.filelike = file
		super().__init__()
	
	def Write(self, me, data, size, processed_size):
		log.debug('Write %d' % size)
		data_arr = ffi.cast('uint8_t*', data)
		buf = bytes(data_arr[0:size])
		#log.debug('data: %s' % buf.decode('ascii'))
		processed_size[0] = self.filelike.write(buf)
		return S_OK

	def Seek(self, me, offset, origin, newposition):
		#log.debug('Seek offset={}; origin={}'.format(offset, origin))
		newpos = self.filelike.seek(offset, origin)
		if newposition != ffi.NULL:
			newposition[0] = newpos
		#log.debug('new position: {}'.format(newpos))
		return S_OK