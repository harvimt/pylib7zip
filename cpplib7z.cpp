#include <cstdio>

//#include <iostream>

#include <fstream>
#include <ios>
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

	//std::wcout << "m_ext: " << m_ext << std::endl;

	//Get File Size
	fseek(m_fd, 0L, SEEK_END);
	m_size = ftell(m_fd);
	fseek(m_fd, 0L, SEEK_SET);
}


C7ZipInStreamFWrapper::C7ZipInStreamFWrapper (FILE* fd, const wstring ext) : m_fd(fd), m_ext(ext) {
	if(!m_fd) return;

	//Get File Size
	fseek(m_fd, 0L, SEEK_END);
	m_size = ftell(m_fd);
	fseek(m_fd, 0L, SEEK_SET);
}

C7ZipInStreamFWrapper::~C7ZipInStreamFWrapper()
{
	fclose(m_fd);
}


int C7ZipInStreamFWrapper::Read(void *data, unsigned int size, unsigned int *processedSize)
{
	if(!m_fd) return 1;

	int count = fread(data, 1, size, m_fd);

	if (processedSize) {
		*processedSize = count;
	}

	if(ferror(m_fd)) return 1;

	return 0;
}


int C7ZipInStreamFWrapper::Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition)
{
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


int C7ZipInStreamFWrapper::GetSize(unsigned __int64 * size)
{
	if(size) *size = m_size;
	return 0;
}


// Out Stream (FD)
C7ZipOutStreamFWrapper::C7ZipOutStreamFWrapper (const string filename)
{
	m_fd = fopen(filename.c_str(), "wb");

	//Get File Size
	fseek(m_fd, 0L, SEEK_END);
	m_size = ftell(m_fd);
	fseek(m_fd, 0L, SEEK_SET);
}


C7ZipOutStreamFWrapper::C7ZipOutStreamFWrapper (FILE* fd): m_fd (fd) { }

C7ZipOutStreamFWrapper::~C7ZipOutStreamFWrapper()
{
	fclose(m_fd);
}


int C7ZipOutStreamFWrapper::Write(const void *data, unsigned int size, unsigned int *processedSize)
{
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


int C7ZipOutStreamFWrapper::Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition)
{
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

