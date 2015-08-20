
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/.")
find_package(Eigen3 REQUIRED)
add_definitions(-std=c++11)
include_directories(${EIGEN3_INCLUDE_DIR})

add_library(anyregistration SHARED anyregistration.cpp)