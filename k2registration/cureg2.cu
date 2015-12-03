#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#include <thrust/iterator/counting_iterator.h>

#include <iostream>
#include "registrationK2.h"

/**
thrust::for_each(
    thrust::make_zip_iterator(
        thrust::make_tuple(map_dist.begin(), undistorted_data.begin(), map_x.begin(), map_yi.begin(),map_c_off.begin())),
    thrust::make_zip_iterator(
        thrust::make_tuple(map_dist.end(),   undistorted_data.end(),   map_x.end(),   map_yi.end(), map_c_off.end())),
        registerxy(...));

*/
struct registerxy
{
    __host__ __device__ 
    registerxy(const thrust::device_vector<float> & depth_data) :
        depth_data_(thrust::raw_pointer_cast(&depth_data[0]))
                {}

    template <typename Tuple>
    __host__ __device__
    void operator()(Tuple t)
    {
        const int index = thrust::get<0>(t);
        if(index < 0)
        {
            thrust::get<1>(t) = 0;
            thrust::get<4>(t) = -1;
        }
        else
        {
            const int size_color_ = 1920*1080;
            const float z = depth_data_[index];
            thrust::get<1>(t) = z; // undistorted
            const float rx = (thrust::get<2>(t) + (color_shift_m_ / z)) * color_fx_ + color_cx_;
            const int cx = rx;
            const int cy = thrust::get<3>(t); // map_yi
            const int c_off = cx + cy * 1920;
            if(c_off < 0 || c_off >= size_color_) {
                 thrust::get<4>(t) = -1;
            }
            else
            {
                 thrust::get<4>(t) = c_off; // in RGB data
            }
        }
    }

    float color_shift_m_;
    float color_fx_;
    float color_cx_;
    const float* depth_data_; // GPU
};

struct registerxy2
{
    __host__ __device__ 
    registerxy2(const thrust::device_vector<float> & depth_data) :
        depth_data_(thrust::raw_pointer_cast(&depth_data[0]))
                {}

    __host__ __device__ 
    registerxy2(const thrust::host_vector<float> & depth_data) :
        depth_data_(thrust::raw_pointer_cast(&depth_data[0]))
                {}

    __host__ __device__
    thrust::tuple<float,int> operator()(thrust::tuple<int,float,float> t)
    {
        const int index = thrust::get<0>(t);
        if(index < 0)
        {
            return thrust::make_tuple(0.0,-1);
        }
        else
        {
            const int size_color_ = 1920*1080;
            const float z = depth_data_[index];
            const float rx = (thrust::get<1>(t) + (color_shift_m_ / z)) * color_fx_ + color_cx_;
            const int cx = rx;
            const int cy = thrust::get<2>(t); // map_yi
            const int c_off = cx + cy * 1920;
            if(c_off < 0 || c_off >= size_color_) {
                 return thrust::make_tuple(z,-1);
            }
            else
            {
                return thrust::make_tuple(z,c_off);
            }
        }
    }

    float color_shift_m_;
    float color_fx_;
    float color_cx_;
    const float* depth_data_; // GPU
};

// TODO Super Filtering: given (cx,cy,z) write minimum z at (cx+-a,cy+-b)
// how is done on GPU....

// Example from ...
// https://github.com/code-iai/iai_kinect2/blob/master/kinect2_registration/src/depth_registration.cl
// in: idx = bufferIndex
//     zImg = bufferImgZ
//     dists = bufferDists filled by project
//     selDist = bufferSelDist filled by project
// in/out:    
//     rendered via idx = bufferRegistered[sizeRegistered] = 

/*
Without binning

fatomicMin(&(depthbuffer[dbindex].depthPrimTag),frag.depthPrimTag);

                            if(frag.depthPrimTag == depthbuffer[dbindex].depthPrimTag)//If this is true, we won the race condition
                                writeToDepthbuffer(x,y,frag, depthbuffer,resolution);

__device__ unsigned long long int fatomicMin(unsigned long long int  * addr, unsigned long long int value)
{
    unsigned long long ret = *addr;
    while(value < ret)
    {
        unsigned long long old = ret;
        if((ret = atomicCAS(addr, old, value)) == old)
            break;
    }
    return ret;

}                                
*/

int main(void)
{
    int w = 512;
    int h = 424;

    libfreenect2::Freenect2Device::IrCameraParams ips;
    libfreenect2::Freenect2Device::ColorCameraParams cps;
    libfreenect2::Registration rk2(ips,cps);

    // TODO init from C++ regular arrays
    thrust::device_vector<int> map_dist(w*h);//= rk2.distort_map;
    thrust::device_vector<int> map_x(w*h);//= depth_to_color_map_x;
    thrust::device_vector<int> map_yi(w*h);//= depth_to_color_map_yi; 

    thrust::device_vector<int> map_c_off(w*h); // output
    thrust::device_vector<int> undistorted_data(w*h); // output

    thrust::host_vector<float> tD(h*w); // depths in
    thrust::device_vector<float> depth_data = tD; // depth in GPU

    registerxy2 rxy(depth_data);
    rxy.color_shift_m_ = cps.shift_m;
    rxy.color_cx_ = cps.cx + 0.5;
    rxy.color_fx_ = cps.fx;

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start, 0);

    // transform form: return tuple
    thrust::transform(
        thrust::make_zip_iterator(thrust::make_tuple(map_dist.begin(), map_x.begin(), map_yi.begin())),
        thrust::make_zip_iterator(thrust::make_tuple(map_dist.end(), map_x.end(), map_yi.end())),
        thrust::make_zip_iterator(thrust::make_tuple(undistorted_data.begin(), map_c_off.begin())),
        rxy);

    /*
    general form without return value
    
        thrust::for_each(
        thrust::make_zip_iterator(
            thrust::make_tuple(map_dist.begin(), undistorted_data.begin(), map_x.begin(), map_yi.begin(),map_c_off.begin())),
        thrust::make_zip_iterator(
            thrust::make_tuple(map_dist.end(),   undistorted_data.end(),   map_x.end(),   map_yi.end(), map_c_off.end())),
            rxy);
    */

    cudaEventRecord(stop, 0);
    cudaEventSynchronize(stop);
    float elapsedTime; 
    cudaEventElapsedTime(&elapsedTime , start, stop);
    printf("Avg. time is %f ms", elapsedTime/100);

    return 0;
}