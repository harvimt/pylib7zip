import lib7zip

def test_get_7z_version():
	assert lib7zip.get_7z_version() == b'9.20'