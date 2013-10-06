import sys
from setuptools import setup
import lib7zip

import re
author = re.match(r'(?P<name>[^<]*) <(?P<email>.*)>', lib7zip.__author__)

setup(
	name='Lib7Zip',
	version=lib7zip.__version__,
	author=author.group('name'),
	author_email=author.group('email'),
	license=lib7zip.__license__,
	description=lib7zip.__doc__,
	long_description=open('README').read(),
	#build settings
	install_requires=['enum34'] if sys.version_info < (3,4) else [],
	packages=['lib7zip', ],
)
