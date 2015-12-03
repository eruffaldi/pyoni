
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

find_package(OpenCVex REQUIRED)
include_directories( ${OpenCV_INCLUDE_DIR} /opt/libjpeg-turbo/include)
link_directories(/opt/libjpeg-turbo/lib64)
add_definitions(--std=c++11)
add_executable(regk2 registrationK2.cpp main.cpp)
target_link_libraries(regk2 ${OpenCV_LIBS} turbojpeg)

find_package(CUDA QUIET REQUIRED)
#set(CUDA_NVCC_FLAGS ${CUDA_NVCC_FLAGS};-O3 -gencode arch=compute_22,code=sm_22)
set(CUDA_NVCC_FLAGS ${CUDA_NVCC_FLAGS};--std=c++11)
#cuda_add_executable(cureg cureg.cu)
#cuda_add_executable(cureg2 cureg2.cu registrationK2.cpp)

add_executable(genall registrationK2.cpp genall.cpp lodepng.cpp)
target_link_libraries(genall ${OpenCV_LIBS} turbojpeg)
