LDFLAGS=-l7zip -ldl -lstdc++
CFLAGS=-std=c99 -ggdb
CXXFLAGS=-std=c++11 -ggdb

all: clib7zip.so pylib7zip.so test test2

clib7zip.so: clib7zip.o

pylib7zip.so: pylib7zip.o clib7zip.o

test: test.o clib7zip.o cpplib7z.o
	gcc -ggdb $(LDFLAGS) -o test test.o clib7zip.o cpplib7z.o

test2: test2.o clib7zip.o cpplib7z.o
	g++ -ggdb $(LDFLAGS) -o test2 test2.o clib7zip.o cpplib7z.o

clean:
	rm -f *.so *.o
