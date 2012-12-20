

// In-Stream io-streams
C7ZipInStreamSWrapper::C7ZipInStreamSWrapper (const string filename)
{
	using namespace std;
	using namespace utf8;

	m_stream = new ifstream(filename.c_str(), ifstream::binary | ifstream::in);

	size_t ext_pos = filename.rfind('.') + 1;
	if(sizeof(wchar_t) == 2) {
		utf8to16(filename.begin() + ext_pos, filename.end(), back_inserter(m_ext));
	}else if(sizeof(wchar_t) == 4){
		utf8to32(filename.begin() + ext_pos, filename.end(), back_inserter(m_ext));
	}

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
