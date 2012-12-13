#include <cstdlib>
#include <cstdio>
#include <cwchar>
#include <iostream>
#include <fstream>
#include <utf8.h>
#include <string>

#define wchartoutf8(a1,a2,a3) if(sizeof(wchar_t) == 2) { utf16to8(a1, a2, a3); }else if(sizeof(wchar_t) == 4){ utf32to8(a1, a2, a3); } else { fprintf(stderr, "#ERROR#"); }
#define utf8towchar(a1,a2,a3) if(sizeof(wchar_t) == 2) { utf8to16(a1, a2, a3); }else if(sizeof(wchar_t) == 4){ utf16to8(a1, a2, a3); } else { fprintf(stderr, "#ERROR#"); }

int main(){
	using namespace std;
	using namespace utf8;

	//print(''.join(r'\U%08x' % ord(x) if ord(x) > 127 else x for x in 'Testing «ταБЬℓσ»: 1<2 & 4+1>3, now 20% off!'))
	const wstring tests[] = {
		L"Testing \u00ab\U000003c4\U000003b1\U00000411\U0000042c\U00002113\U000003c3\U000000bb: 1<2 & 4+1>3, now 20% off!",
		L"\U0001F60E non-bmp characters are cool",
		L"Ace of Spades: \U0001F0A1",
	};

	ofstream out("test.txt", ios::out | ios::binary);
	for(size_t i = 0; i < sizeof(tests)/sizeof(void*); i += 1){
		string s;

		wchartoutf8(tests[i].begin(), tests[i].end(), back_inserter(s));
		
		cout << i << ": " << s << endl;
	}
	return 0;
}
