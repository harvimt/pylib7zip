python-lib7zip
==============
Python bindings for lib7zip_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:author: Mark Harviston <mark.harviston@gmail.com>
:version: 0.1

pylib7zip is a direct binding to 7z.dll from the 7-zip project (7zip.org)

7z.dll uses Windows COM+ calling conventions with an over-engineered slightly pathological 
OOP API.

Currently only works on Windows with Python 3.3

This provides roughly the same functionality as lib7zip does for C++ and SevenZipSharp does for C#
but with a clean Pythonic API.

Like lib7zip getting metadata and extracting files are the only operations supported, creating archives, or updating them in-place is not supported.

This is beta software and may crash if used in an unusual way.

Dependencies
------------

    * 7z.so/7z.dll from http://7zip.org or p7zip on \*Nix
    * CFFI_
    * enum34_

How To Use
----------
By default the path to 7z.dll/7z.so will be autodetected.

.. code:: python

	import io
	from lib7zip import Archive, formats
	#view information on supported formats
	for format in formats:
		print(format.name, ', '.join(format.extensions))
	
	#type of archive will be autodetected
	#pass in optional forceformat argument to force the use a particular format (use the name)
	#pass in optional password argument to open encrypted archives.
	with Archive('path_to.7z') as archive:
		#extract all items to the directory, directory will be created if it doesn't exist
		archive.extract('extract_here')
		
		#list all items in the archive and get their metadata
		for item in archive:
			print( item.isdir, item.path, item.crc)
		
		#extract a particular archive item
		# like extract, accepts a password argument, useful if different
		# items in the archive have different passwords
		archive[0].extract('extract to here.txt')
		
		#extract a particular archive item to a python stream object
		stream = io.BytesIO()
		archive[0].extract(stream)
		stream.getvalue()  # a bytes object containing the contents of item 0

License
-------

This code is licensed under the BSD 2-clause license.

7-Zip is licensed under the LGPL with the exception of the code handling rar compression.

.. _CFFI: https://cffi.readthedocs.org/en/release-0.6/
.. _enum34: https://pypi.python.org/pypi/enum34