#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#include <thrust/iterator/counting_iterator.h>

#include <iostream>

#if 0
typedef thrust::tuple<float,float,float> Float3;

struct DotProduct : public thrust::binary_function<Float3,Float3,float>
{
    const float params[4];
    __host__ __device__
        float operator()(const Float3& a, const Float3& b) const
        {
            return thrust::get<0>(a) * thrust::get<0>(b) +    // x components
                   thrust::get<1>(a) * thrust::get<1>(b) +    // y components
                   thrust::get<2>(a) * thrust::get<2>(b);     // z components
        }
};
#endif

void preparemake3D(const float params[4], thrust::host_vector<float> & tW, thrust::host_vector<float> & tH,int w, int h)
{
    for(int i = 0; i < w; i++)
    {
        tW[i] = (i-params[1]+0.5)/params[0];
    }
    for (int i = 0; i < h; i++)
    {
        tH[i] = -(i-params[3]+0.5)/params[2];
    }
}

// x output = pw[c]*z
// y output = +-ph[c]*z
// z output = z
//
// xyz are coalesced and computed independently
// 1) replicate pw and ph across x and y
// 2) multiply by z


/*
                auto poc = (uint8_t*)(po+3);
                const float rx = pw[c]*z;
                const float ry = w*z;
                po[0] = rx;
                po[1] = -ry;
                po[2] = z;
                poc[0] = pc[2];
                poc[1] = pc[1];
                poc[2] = pc[0];
                good++;
                poi += 3*4+3;
*/

struct unprojectx
{
    __host__ __device__ 
    unprojectx(const thrust::device_vector<float> & p, int w) :p_(thrust::raw_pointer_cast(&p[0])), w_(w) {}
    
    __host__ __device__
    float operator()(const float & d, const int & c)
    {
        return d*p_[c % w_];
    }

    const float * p_;
    const int w_;
};

struct unprojecty
{
    __host__ __device__ 
    unprojecty(const thrust::device_vector<float> & p, int w) :p_(thrust::raw_pointer_cast(&p[0])), w_(w) {}

    __host__ __device__
    float operator()(const float & d, const int & c)
    {
        return d*p_[c / w_];
    }

    const float* p_;
    const int w_;
};

int main(void)
{
    float params[4] = {1,2,3,4}; // fx cx fy cy
    int w = 512;
    int h = 424;
    thrust::host_vector<float> tW(w);
    thrust::host_vector<float> tH(h);

    preparemake3D(params,tW,tH,w,h);

    // Copy host_vector H to device_vector D
    thrust::device_vector<float> dtW = tW,dtH = tH;

    thrust::host_vector<float> tD(h*w); // depths
    thrust::device_vector<float> dtD = tD;
    thrust::device_vector<float> dtPx(h*w); // points (all points)
    thrust::device_vector<float> dtPy(h*w); // points (all points)

    // works on: 1..w by 1..h 
    // input: tD depths
    // output expanded dtP
    // uses dtW and dtH as argument
    thrust::counting_iterator<int> co(0);

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start, 0);
        thrust::transform(dtD.begin(),dtD.end(), co, dtPx.begin(),unprojectx(tW,w)); 
    cudaEventRecord(stop, 0);
    cudaEventSynchronize(stop);
    float elapsedTime; 
    cudaEventElapsedTime(&elapsedTime , start, stop);
    printf("Avg. time is %f ms", elapsedTime/100);

    thrust::transform(dtD.begin(),dtD.end(),co,dtPy.begin(),unprojecty(tH,w));

    // filter by z


    return 0;
}