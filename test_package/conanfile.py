import os

from conans import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.layout import cmake_layout


class DateTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    # VirtualBuildEnv and VirtualRunEnv can be avoided if "tools.env.virtualenv:auto_use" is defined
    # (it will be defined in Conan 2.0)
    generators = "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv" #"CMakeDeps"
    requires = "date/3.0.1@AUTOSOL/stable"
    apply_env = False
    
    def configure(self):
        self.options['date'].header_only = False

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            self.run(".%sexample" % os.sep)