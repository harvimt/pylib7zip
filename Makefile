LDFLAGS=-l7zip -ldl -lstdc++ -g
CFLAGS=-std=c99 -g -Werror -Wextra -Wall
CXXFLAGS=-std=c++11 -g -Werror -Wextra -Wall
#CXXFLAGS=$(CXXFLAGS) -Weffc++ #Add warnings about Scot Meyer's C++
CXX=g++
CC=gcc

all: clib7zip.so test test2

clib7zip.so: clib7zip.o

#pylib7zip.so: pylib7zip.o clib7zip.o

test: test.o clib7zip.o cpplib7z.o
	$(CC) $(LDFLAGS) -o $@ $^

test2: test2.o clib7zip.o cpplib7z.o
	$(CXX) $(LDFLAGS) -o $@ $^

.PHONY: clean
clean:
	rm -f *.so *.o
	rm -f *.bcpp *.bchpp

#Beautiful C++ Style enforcement/correction
beaut: $(patsubst %.cpp, %.bcpp, $(wildcard *.cpp)) $(patsubst %.h, %.bchpp, $(wildcard *.h))
	$(shell $(foreach file, $^, mv $(file) $(patsubst %.bchpp, %.h, $(patsubst %.bcpp, %.cpp, $(file)));))

%.bchpp: %.h
	bcpp $< $@

%.bcpp: %.cpp
	bcpp $< $@
