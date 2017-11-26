#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.34"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/bincrafters/conan-libpng"
    license = "Open source: http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    exports = "FindPNG.cmake"
    exports_sources = ["CMakeLists.txt"]
    description = "libpng is the official PNG reference library. "

    def requirements(self):
        self.requires.add("zlib/1.2.11@conan/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        
    def source(self):
        base_url = "https://sourceforge.net/projects/libpng/files/libpng16/"
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        try:
            tools.download("%s/%s/%s" % (base_url, self.version, zip_name), zip_name)
        except Exception:
            tools.download("%s/older-releases/%s/%s" % (base_url, self.version, zip_name), zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            tools.replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                  'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')
        cmake = CMake(self)
        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("FindPNG.cmake")

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                self.cpp_info.libs = ["png"]
            else:
                if self.options.shared:
                    self.cpp_info.libs = ['libpng16']
                else:
                    self.cpp_info.libs = ['libpng16_static']
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs[0] += "d"
        else:
            self.cpp_info.libs = ["png16d" if self.settings.build_type == "Debug" else "png16"]
            if self.settings.os == "Linux":
                self.cpp_info.libs.append("m")
