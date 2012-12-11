#pragma once

#include <lib7zip.h>
#include <istream>
#include <ostream>

/**
 * Implementation of 7-Zip In Stream based on cstdio File-Pointers (FILE*)
 */
class C7ZipInStreamFWrapper : public C7ZipInStream {
	private:
		wstring m_ext;
		unsigned __int64 m_size;
		FILE* m_fd;

	public:
		C7ZipInStreamFWrapper (const string filename);

		C7ZipInStreamFWrapper (FILE* fd, const wstring ext);

		~C7ZipInStreamFWrapper();

		wstring GetExt() const { return m_ext; }

		int Read(void *data, unsigned int size, unsigned int *processedSize);

		int Seek(__int64 offset, unsigned int seekOrigin, unsigned __int64 *newPosition);

		int GetSize(unsigned __int64 * size);
};

/**
 * Implementation of 7-Zip Out Stream based on cstdio File-Pointers (FILE*)
 */
class C7ZipOutStreamFWrapper : public C7ZipOutStream {
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

		int SetSize(unsigned __int64 size) const { return 0; }; //placebo method, snark, snark

};

/**
 * Implementation of 7-Zip In Stream based on C++ IO std::istream
 */
class C7ZipInStreamSWrapper : public C7ZipInStream {
	private:
		wstring m_ext;
		unsigned __int64 m_size;
		std::istream * m_stream;

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
class C7ZipOutStreamSWrapper : public C7ZipOutStream {
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

		int SetSize(unsigned __int64 size) const { return 0; }; //placebo method, snark, snark

};
