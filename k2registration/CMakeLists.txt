
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

find_package(OpenCVex REQUIRED)
include_directories( ${OpenCV_INCLUDE_DIR} /opt/libjpeg-turbo/include)
link_directories(/opt/libjpeg-turbo/lib64)
add_definitions(--std=c++11)
add_executable(regk2 registrationK2.cpp main.cpp)
target_link_libraries(regk2 ${OpenCV_LIBS} turbojpeg)