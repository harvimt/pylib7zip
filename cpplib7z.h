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
 */

#ifndef CPPLIB7ZIP
#define CPPLIB7ZIP

#include <lib7zip.h>
#include <istream>
#include <ostream>

/**
 * Implementation of 7-Zip In Stream based on cstdio File-Pointers (FILE*)
 */
class C7ZipInStreamFWrapper : public C7ZipInStream
{
	private:
		FILE* m_fd;
		wstring m_ext;
		unsigned __int64 m_size;
		bool owns_pointer;

	public:
		C7ZipInStreamFWrapper (const string filename);

		C7ZipInStreamFWrapper (FILE* fd, const wstring ext);

		virtual ~C7ZipInStreamFWrapper();

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
	private:
		FILE * m_fd;
		int m_size;

	public:
		C7ZipOutStreamFWrapper (const string filename);

		C7ZipOutStreamFWrapper (FILE* fd);

		~C7ZipOutStreamFWrapper();

		int Write(const void *data, unsigned int size, unsigned int *processedSize);

		int Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);

		int GetFileSize() const { return m_size; }

		//placebo method, snark, snark
		int SetSize(unsigned __int64 size) const
		{
			(void)size; return 0;
		};
		//casting a var to void, silences the unnused param error

};

/**
 * Implementation of 7-Zip In Stream based on C++ IO std::istream
 */
class C7ZipInStreamSWrapper : public C7ZipInStream
{
	private:
		std::istream * m_stream;
		wstring m_ext;
		unsigned __int64 m_size;

	public:
		C7ZipInStreamSWrapper (const string filename);

		C7ZipInStreamSWrapper (std::istream * stream, const wstring ext);

		~C7ZipInStreamSWrapper();

		wstring GetExt() const { return m_ext; }

		int Read(void *data, unsigned int size, unsigned int *processedSize);

		int Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);

		int GetSize(unsigned __int64 * size);
};

/**
 * Implementation of 7-Zip Out Stream based on C++ IO std::ostream
 */
class C7ZipOutStreamSWrapper : public C7ZipOutStream
{
	private:
		std::ostream * m_stream;
		int m_size;

	public:
		C7ZipOutStreamSWrapper (const string filename);

		C7ZipOutStreamSWrapper (std::ostream * stream);

		~C7ZipOutStreamSWrapper();

		int Write(const void *data, unsigned int size, unsigned int *processedSize);

		int Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);

		int GetFileSize() const { return m_size; }

		//placebo method, snark, snark
		int SetSize(unsigned __int64 size) const
		{
			(void)size; return 0;
		};
		//casting a var to void, silences the unnused param error

};

#endif
