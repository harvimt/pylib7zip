from distutils.core import setup
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
	packages=['lib7zip', ],
)
