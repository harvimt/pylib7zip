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

import sys, os, os.path
sys.path.append('./build/lib.linux-x86_64-2.7/')

import lib7zip
from lib7zip import NotSupportedArchive
#lib7zip.system("ls")

BASE_PATH = "/media/Media/Games/Game Mods/oblivion/Bash Installers/"

#print("hello");
for filename in os.listdir(BASE_PATH):
	filename = os.path.join(BASE_PATH, filename)
	#if not filename.endswith('.rar'): continue
	if os.path.isdir(filename): continue

	print("opening %s" % filename);

	try:
		archive = lib7zip.openarchive(filename);
	except NotSupportedArchive:
		print("Archive not supported");
		#sys.exit(1);
		continue

	#print("opened archive successfully");

	#print("There are %d item(s) in the archive." % len(archive));

	for item in archive:
		pass

	#print("%d  %s%s  % 10d  %08X  %s" % (item.index, "D" if item.isdir else "F", "E" if item.isencrypted else "U", item.size, item.crc or 0x0, item.path));

	archive.close();
