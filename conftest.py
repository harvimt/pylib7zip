import logging
#logger = logging.getLogger('lib7zip')
logging.basicConfig(
	level=logging.DEBUG,
	#level=logging.INFO,
	format='%(asctime)s - %(name)s::%(funcName)s @ %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
	datefmt='%H:%M',
)
logger = logging.getLogger('lib7zip.simplecom')
logger.setLevel(logging.INFO)
logger = logging.getLogger('lib7zip.stream')
logger.setLevel(logging.INFO)