from setuptools import setup

#with open('README.rst') as f:
#	long_description = f.read()
long_description = 'TODO'

setup(
	name="PyLib7zip",
	version="0.0.dev0",
	url="http://github.com/harvimt/pylib7zip",
    author="Mark Harviston",
	author_email="mark.harviston@gmail.com",
	packages=["lib7zip"],
	licsense='LGPL',
	long_description=long_description,
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["lib7zip/_build.py:ffi"],
    install_requires=["cffi>=1.0.0"],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: LGPL License',
		'Intended Audience :: Developers',
		'Operating System :: Microsoft :: Windows',
		#'Operating System :: MacOS :: MacOS X',
		#'Operating System :: POSIX',
		#'Programming Language :: Python :: 3.3',
		#'Programming Language :: Python :: 3.4',
		#'Programming Language :: Python :: 3.5',
		#'Programming Language :: Python :: 3 :: Only',
	],
)