#Makes clib7zip_test
P7ZIPSOURCE=p7zip_9.20.1
CXXFLAGS=-g -Wall -DUNICODE -D_UNICODE \
	-I. \
	-I$(P7ZIPSOURCE)/CPP \
	-I$(P7ZIPSOURCE)/CPP/7zip/UI/Client7z \
	-I$(P7ZIPSOURCE)/CPP/myWindows \
	-I$(P7ZIPSOURCE)/CPP/include_windows \
	-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE

CFLAGS=-g -Wall \
	-I$(P7ZIPSOURCE)/CPP \
	-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_REENTRANT

LDFLAGS=-ldl

PROG=clib7zip_test
OBJS= \
	clib7zip.o \
	clib7zip_test.o \
	$(P7ZIPSOURCE)/CPP/Common/MyWindows.o \
	$(P7ZIPSOURCE)/CPP/Windows/PropVariant.o

all: clib7zip_test
$(PROG): $(OBJS)
%: %.o
	$(CXX) $(LDFLAGS) $^ -o $@

clean:
	rm -f $(PROG) $(OBJS)
