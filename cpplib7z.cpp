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
 */

#include <cstdio>
#include <utf8.h>//C++ UTF-8 Library
#include "cpplib7z.h"

// In Stream (FD)

C7ZipInStreamFWrapper::C7ZipInStreamFWrapper (const string filename)
{
	using namespace utf8;
	//Open file
	m_fd = fopen(filename.c_str(), "rb");

	if(!m_fd) return;

	//Get Extension
	size_t ext_pos = filename.rfind('.') + 1;
	if(sizeof(wchar_t) == 2) {
		utf8to16(filename.begin() + ext_pos, filename.end(), back_inserter(m_ext));
	}else if(sizeof(wchar_t) == 4){
		utf8to32(filename.begin() + ext_pos, filename.end(), back_inserter(m_ext));
	}

	calc_size();
}


C7ZipInStreamFWrapper::C7ZipInStreamFWrapper (FILE* fd, const wstring ext) : m_fd(fd), m_ext(ext) {
	calc_size();
}

C7ZipInStreamFWrapper::C7ZipInStreamFWrapper (FILE* fd, const string ext) : m_fd(fd) {
	using namespace utf8;

	if(sizeof(wchar_t) == 2) {
		utf8to16(ext.begin(), ext.end(), back_inserter(m_ext));
	}else if(sizeof(wchar_t) == 4){
		utf8to32(ext.begin(), ext.end(), back_inserter(m_ext));
	}

	calc_size();
}

C7ZipInStreamFWrapper::~C7ZipInStreamFWrapper() {
	fclose(m_fd);
}

void C7ZipInStreamFWrapper::calc_size(){
	if(!m_fd) return;

	//Get File Size
	fseek(m_fd, 0L, SEEK_END);
	m_size = ftell(m_fd);
	fseek(m_fd, 0L, SEEK_SET);
}

int C7ZipInStreamFWrapper::Read(void *data, unsigned int size, unsigned int *processedSize) {
	if(!m_fd) return 1;

	int count = fread(data, 1, size, m_fd);

	if (processedSize) {
		*processedSize = count;
	}

	if(ferror(m_fd)) return 1;

	return 0;
}


int C7ZipInStreamFWrapper::Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition) {
	if(!m_fd) return 1;
	if (seekOrigin > 2) {
		return 1;
	}

	fseek(m_fd, offset, seekOrigin);

	if(ferror(m_fd)) {
		return 1;
	}

	if (newPosition != NULL) {
		*newPosition = ftell(m_fd);
		if(ferror(m_fd)) {
			return 1;
		}
	}

	return 0;
}


int C7ZipInStreamFWrapper::GetSize(unsigned __int64 * size) {
	if(size) *size = m_size;
	return 0;
}


// Out Stream (FD)
C7ZipOutStreamFWrapper::C7ZipOutStreamFWrapper (const string filename) {
	m_fd = fopen(filename.c_str(), "wb");

	//Get File Size
	fseek(m_fd, 0L, SEEK_END);
	m_size = ftell(m_fd);
	fseek(m_fd, 0L, SEEK_SET);
}


C7ZipOutStreamFWrapper::C7ZipOutStreamFWrapper (FILE* fd): m_fd (fd) { }

C7ZipOutStreamFWrapper::~C7ZipOutStreamFWrapper() {
	fclose(m_fd);
}


int C7ZipOutStreamFWrapper::Write(const void *data, unsigned int size, unsigned int *processedSize) {
	int count = fwrite(data, 1, size, m_fd);
	if(ferror(m_fd)) {
		return 1;
	}

	if(processedSize) {
		*processedSize = count;
	}

	m_size += count;

	return 0;
}


int C7ZipOutStreamFWrapper::Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition) {
	if(!m_fd) return 1;

	if (seekOrigin > 2) {
		return 1;
	}

	fseek(m_fd, offset, seekOrigin);

	if(ferror(m_fd)) {
		return 1;
	}

	if (newPosition != NULL) {
		*newPosition = ftell(m_fd);
		if(ferror(m_fd)) {
			return 1;
		}
	}

	return 0;
}
