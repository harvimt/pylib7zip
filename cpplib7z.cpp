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

	//Get Extension
	size_t ext_pos = filename.rfind('.') + 1;
	utf8to16(filename.begin() + ext_pos, filename.end(), back_inserter(m_ext));

	//std::wcout << "m_ext: " << m_ext << std::endl;

	//Get File Size
	fseek(m_fd, 0L, SEEK_END);
	m_size = ftell(m_fd);
	fseek(m_fd, 0L, SEEK_SET);
}


C7ZipInStreamFWrapper::C7ZipInStreamFWrapper (FILE* fd, const wstring ext) : m_fd(fd), m_ext(ext) { }

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


// In-Stream io-streams
C7ZipInStreamSWrapper::C7ZipInStreamSWrapper (const string filename)
{
	using namespace std;

	m_stream = new ifstream(filename.c_str(), ifstream::binary | ifstream::in);

	m_stream->seekg (0, ios::end);
	m_size = m_stream->tellg();
	m_stream->seekg (0, ios::beg);
}


C7ZipInStreamSWrapper::C7ZipInStreamSWrapper (std::istream * stream, const wstring ext) : m_stream(stream), m_ext(ext)
{
	using namespace std;

	m_stream->seekg (0, ios::end);
	m_size = m_stream->tellg();
	m_stream->seekg (0, ios::beg);
}


C7ZipInStreamSWrapper::~C7ZipInStreamSWrapper()
{
	delete m_stream;
	m_stream = NULL;
}


int C7ZipInStreamSWrapper::Read(void *data, unsigned int size, unsigned int *processedSize)
{
	m_stream->read(static_cast<char*>(data), size);

	if(m_stream->fail()) {
		return 1;
	}

	if(processedSize) {
		*processedSize = m_stream->gcount();
	}

	return 0;
}


int C7ZipInStreamSWrapper::Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition)
{
	using namespace std;

	static const ios_base::seekdir dir[] = {
		ios::beg,
		ios::cur,
		ios::end
	};

	if (seekOrigin > 0) {
		return 1;
	}

	m_stream->seekg(offset, dir[seekOrigin]);

	if(m_stream->fail()) {
		return 1;
	}

	if (newPosition != NULL) {
		*newPosition = m_stream->tellg();
		if(m_stream->fail()) {
			return 1;
		}
	}

	return 0;
}


int C7ZipInStreamSWrapper::GetSize(unsigned __int64 * size)
{
	if(size) *size = m_size;
	return 0;
}


// Out Stream IO-Streams
C7ZipOutStreamSWrapper::C7ZipOutStreamSWrapper (const string filename) : m_size(0)
{
	using namespace std;
	m_stream = new fstream(filename.c_str(), ios::in | ios::out | ios::binary);
}


C7ZipOutStreamSWrapper::C7ZipOutStreamSWrapper (std::ostream * stream): m_stream(stream), m_size(0) {}

C7ZipOutStreamSWrapper::~C7ZipOutStreamSWrapper()
{
	delete m_stream;
}


int C7ZipOutStreamSWrapper::Write(const void *data, unsigned int size, unsigned int *processedSize)
{
	m_stream->write(static_cast<const char*>(data), size);
	m_stream->flush();

	if(m_stream->fail()) {
		return 1;
	}

	if(processedSize) {
		*processedSize = size;
	}

	return 0;
}


int C7ZipOutStreamSWrapper::Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition)
{
	using namespace std;

	static const ios_base::seekdir dir[] = {
		ios::beg,
		ios::cur,
		ios::end
	};

	if (seekOrigin > 0) {
		return 1;
	}

	m_stream->seekp(offset, dir[seekOrigin]);

	if(m_stream->fail()) {
		return 1;
	}

	if (newPosition != NULL) {
		*newPosition = m_stream->tellp();
		if(m_stream->fail()) {
			return 1;
		}
	}

	return 0;

}
