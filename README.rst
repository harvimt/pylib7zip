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
* 7z.so/7z.dll from 7zip.org
* my fork of lib7zip available on `bitbucket`_

.. _bitbucket: http://google.com


HowTo Use
=========
See test.py for an example, currently only getting (some) info from archives is supported

License
=======
This code is licensed under the BSD 2-clause license.

However, lib7zip is licensed under the MPL and 7zip itself (7z.so/7z.dll)
is licensed under the LGPL (with extra restrictions on the code tht handles rar files).

This shouldn't be a problem since by default all these components are dynamically linked by default. The MPL allows static linking with non-mpl code (even proprietary fcode), so staticly linking lib7zip and pylib7zip together is possible (and potentially the best course of action for many projects).
