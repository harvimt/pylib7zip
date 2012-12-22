/*
 * Copyright (c) 2012, Mark Harviston <mark.harviston@gmail.com>
 * This is free software, most forms of redistribution and derivitive works are permitted with the following restrictions.
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * C++ lib7Zip helpers
 * ===================
 * This file provides implementations on top of C7ZipInStream and C7ZipOutStream on top of POSIX file-descriptors (FILE*)
 *
 */

#ifndef CPPLIB7ZIP
#define CPPLIB7ZIP

#include <lib7zip.h>

/**
 * Implementation of 7-Zip In Stream based on cstdio File-Pointers (FILE*)
 */
class C7ZipInStreamFWrapper : public C7ZipInStream
{
	/*
	 * the file-pointer passed in will be closed automatically when the InStream is destroyed
	 */
	private:
		FILE* m_fd;
		wstring m_ext;
		unsigned __int64 m_size;
		void calc_size();

	public:
		///This constructor has no way of telling you the file failed to open, it's recommended you use the other constructor
		C7ZipInStreamFWrapper (const string filename);

		///Be sure the file is opened in a binary read mode e.g. fopen(filename, "rb")
		C7ZipInStreamFWrapper (FILE* fd, const wstring ext);
		C7ZipInStreamFWrapper (FILE* fd, const string ext);

		~C7ZipInStreamFWrapper();

		wstring GetExt() const { return m_ext; }

		int Read(void *data, unsigned int size, unsigned int *processedSize);

		int Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);

		int GetSize(unsigned __int64 * size);
};

/**
 * Implementation of 7-Zip Out Stream based on cstdio File-Pointers (FILE*)
 */
class C7ZipOutStreamFWrapper : public C7ZipOutStream
{
	/*
	 * the file-pointer passed in will be closed automatically when the OutStream is destroyed
	 */
	private:
		FILE * m_fd;
		int m_size;

	public:
		///This constructor has no way of telling you the file failed to open, it's recommended you use the other constructor
		///However, Opening a file for writing has (slightly) fewer things that can go wrong (if the file doesn't exist it is created)
		C7ZipOutStreamFWrapper (const string filename);

		///Be sure the file is opened in a binary write mode e.g. fopen(filename, "wb")
		C7ZipOutStreamFWrapper (FILE* fd);

		~C7ZipOutStreamFWrapper();

		int Write(const void *data, unsigned int size, unsigned int *processedSize);

		int Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);

		int GetFileSize() const { return m_size; }

		//placebo method, snark, snark
		int SetSize(unsigned __int64 size) const
		{
			(void)size; //casting a var to void, silences the unnused param error
			return 0;
		};
};

#endif
