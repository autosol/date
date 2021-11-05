cmake_minimum_required(VERSION 3.17)
set (CMAKE_BUILD_TYPE Release)
project(PackageTest CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})
set(CMAKE_CXX_STANDARD 17)

if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
  message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
  file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/v0.16.1/conan.cmake"
                "${CMAKE_BINARY_DIR}/conan.cmake"
                EXPECTED_HASH SHA256=396e16d0f5eabdc6a14afddbcfff62a54a7ee75c6da23f32f7a31bc85db23484
                TLS_VERIFY ON)
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
target_include_directories(example
  #PRIVATE ${date_INCLUDE_DIRS_RELEASE})#${CONAN_INCLUDE_DIRS})
  PRIVATE ${CONAN_INCLUDE_DIRS_DATE})
target_link_libraries(example date::date)