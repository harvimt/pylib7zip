import os, os.path

from .comtypes import IID_IUnknown
from .py7ziptypes import IID_ICryptoGetTextPassword, IID_IArchiveOpenCallback, IID_IArchiveOpenVolumeCallback, \
	IID_IArchiveExtractCallback, IID_ISequentialOutStream, IID_ICompressProgressInfo

from .wintypes import S_OK
from .winhelpers import guidp2uuid
from . import log, ffi, wintypes, py7ziptypes
from .simplecom import IUnknownImpl
from .stream import FileOutStream

class ArchiveExtractCallback(IUnknownImpl):
	"""
		Base class for extract callbacks
	"""
	GUIDS = {
		IID_IArchiveExtractCallback: 'IArchiveExtractCallback',
		IID_ICryptoGetTextPassword: 'ICryptoGetTextPassword',
		IID_ICompressProgressInfo: 'ICompressProgressInfo',
	}
	
	def __init__(self, password=''):
		#self.out_file = FileOutStream(file)
		self.password = ffi.new('wchar_t[]', password)
		super().__init__()

	#HRESULT(*SetTotal)(void* self, uint64_t total);
	def SetTotal(self, me, total):
		log.debug('SetTotal %d' % total)
		return S_OK
	
	#HRESULT(*SetCompleted)(void* self, const uint64_t *completeValue);
	def SetCompleted(self, me, completeValue):
		if completeValue:
			log.debug('SetCompleted: %d' % int(completeValue[0]))
		else:
			log.debug('SetCompleted: NULL')
		return S_OK
	
	#HRESULT(*GetStream)(void* self, uint32_t index, ISequentialOutStream **outStream,  int32_t askExtractMode);
	def GetStream(self, me, index, outStream, askExtractMode):
		log.debug('GetStream')
		raise NotImplemented
		#outStream[0] = self.out_file.instances[IID_ISequentialOutStream]
		return S_OK
	
	#HRESULT(*PrepareOperation)(void* self, int32_t askExtractMode);
	def PrepareOperation(self, me, askExtractMode):
		log.debug('PrepareOperation, askExtractMode=%d' % int(askExtractMode))
		return S_OK
		
	#HRESULT(*SetOperationResult)(void* self, int32_t resultEOperationResult);
	def SetOperationResult(self, me, operational_result):
		log.debug('Operational Result: %d' % int(operational_result))
		return S_OK

	def CryptoGetTextPassword(self, me, password):
		log.debug('GetPassword')
		password[0] = self.password
		return S_OK
	
	#STDMETHOD(SetRatioInfo)(const UInt64 *inSize, const UInt64 *outSize) PURE;
	def SetRatioInfo(self, me, in_size, out_size):
		log.debug('SetRatioInfo: in_size=%d, out_size=%d' % (int(in_size[0]), int(out_size[0])))
		return S_OK

class ArchiveExtractToDirectoryCallback(ArchiveExtractCallback):
	"""
		each item is extracted to the given directory based on it's path.
	"""
	def __init__(self, archive, directory='', password=''):
		self.directory = directory
		self.archive = archive
		self._streams = []
		super().__init__(password)
	
	def GetStream(self, me, index, outStream, askExtractMode):
		log.debug('GetStream')
		path = os.path.join(self.directory,self.archive[index].path)
		dirname = os.path.dirname(path)
		if dirname and not os.path.exists(dirname):
			os.makedirs(dirname)
		
		stream = FileOutStream(path)
		outStream[0] = stream.instances[IID_ISequentialOutStream]
		return S_OK
	
	def flush_and_close_streams(self):
		for stream in self._streams:
			stream.filelike.flush()
			stream.filelike.close()
		
class ArchiveExtractToStreamCallback(ArchiveExtractCallback):
	"""
		Extract all files to the same stream (most useful for extracting one file)
	"""
	def __init__(self, stream, index, password=''):
		self.index = index
		self.stream = FileOutStream(stream)
		super().__init__(password)
		
	def GetStream(self, me, index, outStream, askExtractMode):
		log.debug('GetStream')
		if self.index == index:
			log.debug('index found')
			outStream[0] = self.stream.instances[py7ziptypes.IID_ISequentialOutStream]
			return S_OK
		else:
			log.debug('index not found')
			outStream[0] = ffi.NULL
			return 1