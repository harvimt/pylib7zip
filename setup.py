#!/usr/bin/python2
# Copyright (c) 2012, Mark Harviston <mark.harviston@gmail.com>
# This is free software, most forms of redistribution and derivitive works are permitted with the following restrictions.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from distutils.core import setup, Extension

lib7zip_mod = Extension('lib7zip',
		libraries=['7zip','dl'],
		extra_cflags=['-Wno-write-strings'],
		sources = ['pylib7zip.cpp', 'cpplib7z.cpp'])

with open("README.rst") as readme:
	setup (name = 'Lib7zip',
		version = '0.1',
		author = "Mark Harviston",
		author_email = "mark.harviston@gmail.com",
		description = 'Python Bindings to lib7zip, for accessing various archive formats.',
		long_description = readme.read(),
		ext_modules = [lib7zip_mod])
