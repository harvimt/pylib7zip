#include <string>
#include <iostream>
#include <clocale>
#include <locale>
#include <vector>

#include <utf8.h>

using namespace std;

int main() {
	//std::cout << "Start!" << std::endl;
	std::setlocale(LC_ALL, "");
	const std::wstring ws = L"ħëłlö";
	std::string utf8str;

	utf8::utf16to8(ws.begin(), ws.end(), back_inserter(utf8str));

	cout << utf8str << endl;
}
