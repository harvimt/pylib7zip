import os, os.path

from .py7ziptypes import IID_ICryptoGetTextPassword, IID_IArchiveExtractCallback, \
	IID_ISequentialOutStream, IID_ICompressProgressInfo, IID_ICryptoGetTextPassword2, \
	OperationResult, AskMode

from .wintypes import HRESULT
from . import log, ffi, C, py7ziptypes
from .simplecom import IUnknownImpl
from .stream import FileOutStream

class ArchiveExtractCallback(IUnknownImpl):
	"""
		Base class for extract callbacks
	"""
	GUIDS = {
		IID_IArchiveExtractCallback: 'IArchiveExtractCallback',
		IID_ICryptoGetTextPassword: 'ICryptoGetTextPassword',
		IID_ICryptoGetTextPassword2: 'ICryptoGetTextPassword2',
		IID_ICompressProgressInfo: 'ICompressProgressInfo',
	}
	
	def __init__(self, password=''):
		#self.out_file = FileOutStream(file)
		#self.password = ffi.new('char[]', (password or '').encode('ascii'))
		self.password = ffi.new('wchar_t[]', password or '')
		#password = password or ''
		'''
		self._password = ffi.gc(C.malloc(ffi.sizeof('wchar_t') * len(password) + 1), C.free)
		self.password = ffi.cast('wchar_t*', self._password)
		self.password[0:len(password)] = password
		self.password[len(password)] = '\0'
		'''
		
		super().__init__()
	
	def cleanup(self):
		pass

	#HRESULT(*SetTotal)(void* self, uint64_t total);
	def SetTotal(self, me, total):
		log.info('SetTotal %d' % total)
		return HRESULT.S_OK.value
	
	#HRESULT(*SetCompleted)(void* self, const uint64_t *completeValue);
	def SetCompleted(self, me, completeValue):
		if completeValue:
			log.info('SetCompleted: %d' % int(completeValue[0]))
		else:
			log.info('SetCompleted: NULL')
		return HRESULT.S_OK.value
	
	#HRESULT(*GetStream)(void* self, uint32_t index, ISequentialOutStream **outStream,  int32_t askExtractMode);
	def GetStream(self, me, index, outStream, askExtractMode):
		log.debug('GetStream')
		raise NotImplemented
	
	#HRESULT(*PrepareOperation)(void* self, int32_t askExtractMode);
	def PrepareOperation(self, me, askExtractMode):
		log.info('PrepareOperation, askExtractMode=%d' % int(askExtractMode))
		return HRESULT.S_OK.value
		
	#HRESULT(*SetOperationResult)(void* self, int32_t resultEOperationResult);
	def SetOperationResult(self, me, operational_result):
		res = OperationResult(int(operational_result))
		if res == OperationResult.kOK:
			log.info('Operational Result: %s', res.name)
		else:
			log.warn('Operational Result: %s', res.name)

		self.cleanup()
		return HRESULT.S_OK.value

	def CryptoGetTextPassword(self, me, password):
		log.debug('CryptoGetTextPassword me=%r password=%r%r', me, ffi.string(self.password), self.password)
		assert password[0] == ffi.NULL
		#log.debug('passowrd?=%s', ffi.string(password[0]))
		#password = ffi.cast('wchar_t**', password)
		password[0] = self.password
		#password[0] = ffi.NULL
		log.debug('CryptoGetTextPassword returning, password=%s', ffi.string(password[0]))
		return HRESULT.S_OK.value
		#return len(self.password)

	def CryptoGetTextPassword2(self, me, isdefined, password):
		log.debug('CryptoGetTextPassword2 me=%r password=%r%r', me, ffi.string(self.password), self.password)
		isdefined[0] = bool(self.password)
		password[0] = self.password
		log.debug('CryptoGetTextPassword returning, password=%s', ffi.string(password[0]))
		return HRESULT.S_OK.value

	#STDMETHOD(SetRatioInfo)(const UInt64 *inSize, const UInt64 *outSize) PURE;
	def SetRatioInfo(self, me, in_size, out_size):
		log.debug('SetRatioInfo: in_size=%d, out_size=%d' % (int(in_size[0]), int(out_size[0])))
		return HRESULT.S_OK.value
	

class ArchiveExtractToDirectoryCallback(ArchiveExtractCallback):
	"""
		each item is extracted to the given directory based on it's path.
	"""
	def __init__(self, archive, directory='', password=''):
		self.directory = directory
		self.archive = archive
		self._streams = []
		#self._cleaned_up = False
		super().__init__(password)
	
	def GetStream(self, me, index, outStream, askExtractMode):
		askExtractMode = AskMode(askExtractMode)
		log.debug('GetStream(%d, -, %d)', index, askExtractMode)

		if askExtractMode != AskMode.kExtract:
			return HRESULT.S_OK.value

		
		path = os.path.join(self.directory, self.archive[index].path)
		dirname = os.path.dirname(path)
		log.debug('extracting to: %s', path)
		
		if self.archive[index].isdir:
			os.makedirs(path, exist_ok=True)
			outStream[0] = ffi.NULL
		else:
			os.makedirs(dirname, exist_ok=True)
			stream = FileOutStream(path)
			self._streams.append(stream)
			outStream[0] = stream.instances[IID_ISequentialOutStream]
		return HRESULT.S_OK.value
	
	def cleanup(self):
		log.debug('flushing streams')
		#if self._cleaned_up:
		#	return
		
		for stream in self._streams:
			#TODO? stream.Release()
			stream.filelike.flush()
			stream.filelike.close()

		self._streams = []
		self._cleaned_up = True
		log.debug('streams flushed & closed')

class ArchiveExtractToStreamCallback(ArchiveExtractCallback):
	"""
		Extract all files to the same stream (most useful for extracting one file)
	"""
	def __init__(self, stream, index, password=''):
		self.index = index
		self.stream = FileOutStream(stream)
		super().__init__(password)
		
	def GetStream(self, me, index, outStream, askExtractMode):
		askExtractMode = AskMode(askExtractMode)
		log.debug('GetStream(%d, -, %d)', index, askExtractMode)

		if askExtractMode != AskMode.kExtract:
			return HRESULT.S_OK.value

		if self.index == index:
			outStream[0] = self.stream.instances[py7ziptypes.IID_ISequentialOutStream]
			return HRESULT.S_OK.value
		else:
			log.debug('index not found')
			outStream[0] = ffi.NULL
			return HRESULT.S_OK.value