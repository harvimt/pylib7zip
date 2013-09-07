from .comtypes import IID_IUnknown
from .py7ziptypes import IID_ICryptoGetTextPassword, IID_IArchiveOpenCallback, IID_IArchiveOpenVolumeCallback, \
	IID_IArchiveExtractCallback, IID_ISequentialOutStream, IID_ICompressProgressInfo

from .wintypes import guidp2uuid, S_OK
from . import log, ffi, wintypes
from .simplecom import IUnknownImpl
from .stream import FileOutStream

class ArchiveExtractCallback(IUnknownImpl):
	GUIDS = {
		IID_IArchiveExtractCallback: 'IArchiveExtractCallback',
		IID_ICryptoGetTextPassword: 'ICryptoGetTextPassword',
		IID_ICompressProgressInfo: 'ICompressProgressInfo',
	}
	
	def __init__(self, password=''):
		self.out_file = FileOutStream('out.txt')
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
		outStream[0] = self.out_file.instances[IID_ISequentialOutStream]
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