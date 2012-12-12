LDFLAGS=-l7zip -ldl -lstdc++
CFLAGS=-std=c99 -ggdb -Werror -Wextra -Wall
CXXFLAGS=-std=c++11 -ggdb -Werror -Wextra -Wall
#CXXFLAGS=$(CXXFLAGS) -Weffc++ #Add warnings about Scot Meyer's C++

all: clib7zip.so pylib7zip.so test test2

clib7zip.so: clib7zip.o

pylib7zip.so: pylib7zip.o clib7zip.o

test: test.o clib7zip.o cpplib7z.o
	gcc -ggdb $(LDFLAGS) -o $@ $^

test2: test2.o clib7zip.o cpplib7z.o
	g++ -ggdb $(LDFLAGS) -o $@ $^

clean:
	rm -f *.so *.o
	rm -f *.bcpp *.bchpp

#Beautiful C++ Style enforcement/correction
beaut: $(patsubst %.cpp, %.bcpp, $(wildcard *.cpp)) $(patsubst %.h, %.bchpp, $(wildcard *.h))

%.bchpp: %.h
	bcpp $< $@

%.bcpp: %.cpp
	bcpp $< $@
