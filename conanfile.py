#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import gzip
from conans import ConanFile, tools, CMake


class LibpngConan(ConanFile):
    name = "libpng-apng"
    version = "1.6.36"
    description = "libpng is the official PNG file format reference library."
    url = "http://github.com/bincrafters/conan-libpng"
    author = "Bincrafters <bincrafters@gmail.com>"
    homepage = "http://www.libpng.org"
    license = "http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires.add("zlib/1.2.11@conan/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        base_url = "https://sourceforge.net/projects/libpng/files/libpng16/"
        # Don't use .xz, CIs uses conan/python2, which does not support xz
        tools.get(
            "%s/%s/libpng-%s.tar.gz" % (base_url, self.version, self.version),
            sha256="ca13c548bde5fb6ff7117cc0bdab38808acb699c0eccb613f0e4697826e1fd7d")
        os.rename("libpng-" + self.version, self._source_subfolder)

        # APNG patch
        patch_base_url = "https://sourceforge.net/projects/libpng-apng/files/libpng16/"
        tools.download(
            "%s/%s/libpng-%s-apng.patch.gz" % (patch_base_url, self.version, self.version),
            "libpng-apng.patch.gz")
        tools.check_sha1("libpng-apng.patch.gz", "a08f3d348dd10882b8a81544b56e53618fb8921e")
        with gzip.open("libpng-apng.patch.gz", "rb") as f:
            patch = f.read().decode()
        tools.patch(base_path=self._source_subfolder, patch_string=patch, strip=1)

        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            tools.replace_in_file("%s/CMakeListsOriginal.txt" % self._source_subfolder,
                                  'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                  'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')
        # do not use _static suffix on VS
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            tools.replace_in_file("%s/CMakeListsOriginal.txt" % self._source_subfolder,
                                  'OUTPUT_NAME "${PNG_LIB_NAME}_static',
                                  'OUTPUT_NAME "${PNG_LIB_NAME}')

        if self.settings.build_type == 'Debug':
            tools.replace_in_file(os.path.join(self._source_subfolder, 'libpng.pc.in'),
                                  '-lpng@PNGLIB_MAJOR@@PNGLIB_MINOR@',
                                  '-lpng@PNGLIB_MAJOR@@PNGLIB_MINOR@d')

        if 'arm' in self.settings.arch and self.settings.os == "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeListsOriginal.txt'),
                                  'PATHS /usr/lib /usr/local/lib',
                                  'PATHS /usr/lib /usr/local/lib /usr/arm-linux-gnueabihf/lib /usr/arm-linux-gnueabi/lib ')

        cmake = CMake(self)

        cmake.definitions['CMAKE_INSTALL_LIBDIR'] = 'lib'
        cmake.definitions['CMAKE_INSTALL_BINDIR'] = 'bin'
        cmake.definitions['CMAKE_INSTALL_INCLUDEDIR'] = 'include'

        cmake.definitions["PNG_TESTS"] = "OFF"
        cmake.definitions["PNG_SHARED"] = self.options.shared
        cmake.definitions["PNG_STATIC"] = not self.options.shared
        cmake.definitions["PNG_DEBUG"] = "OFF" if self.settings.build_type == "Release" else "ON"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        shutil.rmtree(os.path.join(self.package_folder, 'share', 'man'), ignore_errors=True)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                self.cpp_info.libs = ["png"]
            else:
                self.cpp_info.libs = ['libpng16']
        else:
            self.cpp_info.libs = ["png16"]
            if self.settings.os == "Linux":
                self.cpp_info.libs.append("m")
        # use 'd' suffix everywhere except mingw
        if self.settings.build_type == "Debug" and not (self.settings.os == "Windows" and self.settings.compiler == "gcc"):
            self.cpp_info.libs[0] += "d"
