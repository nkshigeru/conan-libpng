#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.34"
    description = "libpng is the official PNG file format reference library. "
    url="http://github.com/bincrafters/conan-libpng"
    website = "http://www.libpng.org"
    license = "http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires.add("zlib/1.2.11@conan/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        
    def source(self):
        base_url = "https://sourceforge.net/projects/libpng/files/libpng16/"
        try:
            tools.get("%s/%s/libpng-%s.tar.gz" % (base_url, self.version, self.version))
        except Exception:
            tools.get("%s/older-releases/%s/libpng-%s.tar.gz" % (base_url, self.version, self.version))
        os.rename("libpng-" + self.version, self.source_subfolder)
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            tools.replace_in_file("%s/CMakeListsOriginal.txt" % self.source_subfolder, 'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                  'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')
        cmake = CMake(self)
        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        shutil.rmtree(os.path.join(self.package_folder, 'share', 'man'), ignore_errors=True)
        try:
            os.rename(os.path.join(self.package_folder, "lib", "libpng16_static.lib"),
                      os.path.join(self.package_folder, "lib", "libpng16.lib"))
        except:
            pass

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                self.cpp_info.libs = ["png"]
            else:
                self.cpp_info.libs = ['libpng16']
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs[0] += "d"
        else:
            self.cpp_info.libs = ["png16d" if self.settings.build_type == "Debug" else "png16"]
            if self.settings.os == "Linux":
                self.cpp_info.libs.append("m")
