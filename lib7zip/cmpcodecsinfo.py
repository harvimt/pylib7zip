import logging
log = logging.getLogger(__name__)

from .py7ziptypes import IID_ICompressCodecsInfo
from .simplecom import IUnknownImpl
from . import ffi, methods, dll7z
from .wintypes import HRESULT
from .winhelpers import uuid2guidp


class CompressCodecsInfo(IUnknownImpl):
	GUIDS = {
		IID_ICompressCodecsInfo: 'ICompressCodecsInfo',
	}

	def GetNumberOfMethods(self, me, numMethods):
		log.debug('Info.GetNumberOfMethods')
		return dll7z.GetNumberOfMethods(numMethods)

	def GetProperty(self, me, index, propID, value):
		log.debug('Info.GetProperty')
		return dll7z.GetMethodProperty(index, propID, value)

	def CreateDecoder(self, me, index, iid, coder):
		log.debug('Info.CreateDecoder')
		classid = uuid2guidp(methods[index].decoder)
		return dll7z.CreateObject(classid, iid, coder)

	def CreateEncoder(self, me, index, iid, coder):
		log.debug('Info.CreateEncoder')
		classid = uuid2guidp(methods[index].encoder)
		return dll7z.CreateObject(classid, iid, coder)
