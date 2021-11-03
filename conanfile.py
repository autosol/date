from conans import ConanFile, CMake, tools
#from conan.tools.cmake import CMakeToolchain, CMake
#from conan.tools.layout import cmake_layout
import os

required_conan_version = ">=1.33.0"

#Adapted from https://conan.io/center/date?tab=recipe
class DateConan(ConanFile):
    name = "date"
    version = "3.0.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HowardHinnant/date"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    topics = ("date", "datetime", "timezone",
              "calendar", "time", "iana-database")
    license = "MIT"
    requires = "libarchive/3.5.1", "libcurl/7.78.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "use_system_tz_db": [True, False],
        "use_tz_db_in_dot": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "use_system_tz_db": False,
        "use_tz_db_in_dot": False,
    }
    exports_sources = ["CMakeLists.txt","src/*","include/*","cmake/*"]
    #exports_sources = "*"
    keep_imports = True
    
    generators = "cmake", "cmake_find_package"
    _cmake = None
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["iOS", "tvOS", "watchOS"]:
            self.options.use_system_tz_db = True
            
    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):        
        if not self.options.header_only and not self.options.use_system_tz_db:
            self.requires("libcurl/7.78.0")
            self.requires("libarchive/3.5.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")
        
    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    #def source(self):
        #self.run("git clone --depth 1 https://github.com/autosol/date.git")
        #self.run("git clone --depth 1 file:///C/Code/autosol_date/.git date")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
        cmake.definitions["BUILD_TZ_LIB"] = not self.options.header_only
        # workaround for clang 5 not having string_view
        if tools.Version(self.version) >= "3.0.0" and self.settings.compiler == "clang" \
                and tools.Version(self.settings.compiler.version) <= "5.0":
            cmake.definitions["DISABLE_STRING_VIEW"] = True
        cmake.configure()

        self._cmake = cmake
        return self._cmake

    def build(self):
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()
            
    #def imports(self):
        #self.copy("*")
            
    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses")
        #self.copy("*")

        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "date"
        self.cpp_info.names["cmake_find_package_multi"] = "date"

        # date-tz
        if not self.options.header_only:
            self.cpp_info.components["date-tz"].names["cmake_find_package"] = "date-tz"
            self.cpp_info.components["date-tz"].names["cmake_find_package_multi"] = "date-tz"
            lib_name = "{}tz".format("date-" if tools.Version(self.version) >= "3.0.0" else "")
            self.cpp_info.components["date-tz"].libs = [lib_name]
            if self.settings.os == "Linux":
                self.cpp_info.components["date-tz"].system_libs.append("pthread")

            if not self.options.use_system_tz_db:
                self.cpp_info.components["date-tz"].requires.append("libcurl::libcurl")
                self.cpp_info.components["date-tz"].requires.append("libarchive::libarchive")

            if self.options.use_system_tz_db and not self.settings.os == "Windows":
                use_os_tzdb = 1
            else:
                use_os_tzdb = 0

            defines = ["USE_OS_TZDB={}".format(use_os_tzdb)]
            if self.settings.os == "Windows" and self.options.shared:
                defines.append("DATE_USE_DLL=1")

            self.cpp_info.components["date-tz"].defines.extend(defines)

