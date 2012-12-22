cmake_minimum_required (VERSION 2.6)
project(clib7zip)

#include_directories("." "C:/Program Files (x86)/lib7zip/include")
#link_directories("C:/Program Files (x86)/lib7zip/lib")

add_definitions("-g -Werror -Wall -Wextra")
add_definitions("-D_BSD_SOURCE -O2")
SET(CMAKE_C_FLAGS "-std=c99")

add_library(c7zip_static STATIC clib7zip.cpp cpplib7z.cpp)
add_library(c7zip SHARED clib7zip.cpp cpplib7z.cpp)
target_link_libraries(c7zip 7zip)

add_executable(ctest ctest.c)
target_link_libraries(ctest c7zip 7zip dl)

add_executable(cpptest cpptest.cpp)
target_link_libraries(cpptest c7zip 7zip dl)

install (FILES clib7zip.h DESTINATION include/)
install (TARGETS c7zip_static c7zip DESTINATION lib/)
