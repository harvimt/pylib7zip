==============
Python-lib7Zip
==============
Python Bindings to lib7zip
==========================
:Author: Mark Harvistion <mark.harviston@gmail.com>

pylib7zip is a binding for the c++ api lib7zip
which is in turn a wrapper over 7z.so/7z.dll which is a C API that
uses Windows COM+ conventions (and written in C++)

Dependencies
============
* 7z.so/7z.dll from `7zip.org`_
* my fork of `lib7zip`_ available on `bitbucket`_
* `utf8-cpp`_ (utf8.h)

.. _bitbucket: http://bitbucket.org/infinull/lib7zip
.. _7zip.org: http://7zip.org
.. _lib7zip: https://code.google.com/p/lib7zip/
.. _utf8-cpp: http://utfcpp.sourceforge.net/

How To Use
==========
See pytests.py for an example, currently only getting (some) info from archives is supported

CFFI & CTypes
=============
There is a ctypes and cffi binding to clib7zip.cpp, this file can be copmiled with `cmake`.
For ease-of-use on my part, ctypes or cffi + a C binding may be the future of this module.

so far, CFFI seems somewhat, but not drastically easier to use, but also somewhat slower than ctypes,
but it shouldn't be, so there's probably something wrong with my code?

(not that the pylib7zip.cpp was ever really "done").

Since libc7zip, (c bindings to lib7zip) is useful in it's own right, and other devs may wish to use it,
it may get moved to it's own module, or merged with my port of lib7zip.

License
=======
This code is licensed under the BSD 2-clause license.

However, lib7zip is licensed under the MPL and 7zip itself (7z.so/7z.dll)
is licensed under the LGPL (with extra restrictions on the code tht handles rar files).

This shouldn't be a problem since by default all these components are dynamically linked by default. The MPL allows static linking with non-mpl code (even proprietary fcode), so staticly linking lib7zip and pylib7zip together is possible (and potentially the best course of action for many projects).
