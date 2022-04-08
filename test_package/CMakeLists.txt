cmake_minimum_required(VERSION 3.17)
set (CMAKE_BUILD_TYPE Release)
project(PackageTest CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})
set(CMAKE_CXX_STANDARD 17)

set(CONAN_SYSTEM_INCLUDES ON) #Hide warnings from libraries

message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/0.18.1/conan.cmake"
	"${CMAKE_BINARY_DIR}/conan.cmake"
	EXPECTED_HASH SHA256=5cdb3042632da3efff558924eecefd580a0e786863a857ca097c3d1d43df5dcd
	TLS_VERIFY ON
	STATUS DOWNLOAD_STATUS)
		
list(GET DOWNLOAD_STATUS 0 DOWNLOAD_STATUS_CODE)
if(NOT ${DOWNLOAD_STATUS_CODE} EQUAL 0)
	message(FATAL_ERROR "Error downloading conan.cmake: ${DOWNLOAD_STATUS}")
else()
	message(STATUS "Download result: ${DOWNLOAD_STATUS}")
endif()

if(CONAN_EXPORTED) # in conan local cache
	include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
	conan_basic_setup()
else() # in user space
	include(${CMAKE_BINARY_DIR}/conan.cmake)

	conan_cmake_run(CONANFILE conanfile.py
					BASIC_SETUP
					BUILD missing)
endif()

include(${CMAKE_BINARY_DIR}/conan.cmake)

find_package(date CONFIG REQUIRED)

add_executable(example src/example.cpp)
#include_directories(${CONAN_INCLUDE_DIRS})
target_include_directories(example
  PRIVATE ${CONAN_INCLUDE_DIRS_DATE})
target_link_libraries(example date::date)