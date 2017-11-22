project(cmake_wrapper)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

add_subdirectory(libpng-1.6.34)
