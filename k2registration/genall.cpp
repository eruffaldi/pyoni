#include <iostream>
#include <vector>
#include "registrationK2.h"
#include <array>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include <fstream>
#include <chrono>
#include "lodepng.h"
#include <arpa/inet.h>
template <class T=std::chrono::high_resolution_clock>
class TimerT
{
public:
	TimerT() : start(T::now()) {}
	void stop() { end = T::now(); }
    std::chrono::time_point<T> start, end;

    double us() const 
    {
    	 return std::chrono::duration_cast<std::chrono::microseconds>(end-start).count();
    }
};

using Timer = TimerT<>;

template <class T>
std::ostream & operator << (std::ostream & ons, const TimerT<T> & x)
{
	ons << x.us() << "us";
	return ons;
}


using namespace libfreenect2;

#include <turbojpeg.h>

void decodejpeg(const uint8_t * input, int inputsize, int w, int h, uint8_t * output, int format = TJPF_BGRX)
{
tjhandle decompressor = tjInitDecompress();
int r = tjDecompress2(decompressor, (uint8_t*)input, inputsize, output, w, w * tjPixelSize[format], h, format, 0);
tjDestroy(decompressor) ;
}



template <class T>
struct FrameT : public libfreenect2::Frame
{
	FrameT(std::array<int,2> size) : FrameT(size[0],size[1]) {}

	FrameT(int w, int h) 
	{
		width = w;
		height = h;
		bytes_per_pixel = sizeof(T);
		data_.resize(w*h);
		data = &data_[0];
	}

	std::vector<T> data_;
};

void fillin(Freenect2Device::IrCameraParams &depth_p, Freenect2Device::ColorCameraParams &rgb_p)
{

	// from text file
	float depth_cx = 253.9832;
    float depth_cy = 211.093994;
    float depth_depth_q = 0.00999999978;
    float depth_fx = 365.150208;
    float depth_fy = 365.150208;
    float depth_k1 = 0.0922871977;
    float depth_k2 = -0.266797304;
    float depth_k3 = 0.0901915208;



    float color_color_q = 0.00219899998;
    float color_cx = 959.5;
    float color_cy = 539.5;
    float color_fx = 1081.37207;
    float color_fy = 1081.37207;
    float color_mx_x0y0 = 0.152766302;
    float color_mx_x0y1 = 0.00462980801;
    float color_mx_x0y2 = -8.62425368e-05;
    float color_mx_x0y3 = 2.66473307e-05;
    float color_mx_x1y0 =0.640707493;
    float color_mx_x1y1 = 0.000260630302;
    float color_mx_x1y2 = 0.000386019994;
    float color_mx_x2y0 = -8.80247826e-05;
    float color_mx_x2y1 = 7.26420622e-05;
    float color_mx_x3y0 = 0.000523260387;
    float color_my_x0y0 = 0.035591729;
    float color_my_x0y1 = 0.640462875;
    float color_my_x0y2 = 0.000211564999;
    float color_my_x0y3 = 0.000705449376;
    float color_my_x1y0 = -0.00469533494;
    float color_my_x1y1 = 6.66987689e-05;
    float color_my_x1y2 = 3.74624688e-05;
    float color_my_x2y0 = -9.42075494e-05;
    float color_my_x2y1 = 0.000468305807;
    float color_my_x3y0 = 1.641368e-05;
    float color_shift_m = 52;
    float color_shift_d = 863;

    depth_p.fx = depth_fx;
depth_p.fy = depth_fy;
depth_p.cx = depth_cx;
depth_p.cy = depth_cy;
depth_p.k1 = depth_k1;
depth_p.k2 = depth_k2;
depth_p.k3 = depth_k3;
depth_p.p1 = 0;
depth_p.p2 = 0;
rgb_p.fx = color_fx;
rgb_p.fy = color_fy;
rgb_p.cx = color_cx;
rgb_p.cy = color_cy;
rgb_p.shift_d = color_shift_d;
rgb_p.shift_m = color_shift_m;
rgb_p.mx_x3y0 = color_mx_x3y0;
rgb_p.mx_x0y3 = color_mx_x0y3;
rgb_p.mx_x2y1 = color_mx_x2y1;
rgb_p.mx_x1y2 = color_mx_x1y2;
rgb_p.mx_x2y0 = color_mx_x2y0;
rgb_p.mx_x0y2 = color_mx_x0y2;
rgb_p.mx_x1y1 = color_mx_x1y1;
rgb_p.mx_x1y0 = color_mx_x1y0;
rgb_p.mx_x0y1 = color_mx_x0y1;
rgb_p.mx_x0y0 = color_mx_x0y0;
rgb_p.my_x3y0 = color_my_x3y0;
rgb_p.my_x0y3 = color_my_x0y3;
rgb_p.my_x2y1 = color_my_x2y1;
rgb_p.my_x1y2 = color_my_x1y2;
rgb_p.my_x2y0 = color_my_x2y0;
rgb_p.my_x0y2 = color_my_x0y2;
rgb_p.my_x1y1 = color_my_x1y1;
rgb_p.my_x1y0 = color_my_x1y0;
rgb_p.my_x0y1 = color_my_x0y1;
rgb_p.my_x0y0 = color_my_x0y0;

}

#if 0
// Alternative lookup based
  void createLookup(size_t width, size_t height)
  {
    const float fx = 1.0f / cameraMatrixColor.at<double>(0, 0);
    const float fy = 1.0f / cameraMatrixColor.at<double>(1, 1);
    const float cx = cameraMatrixColor.at<double>(0, 2);
    const float cy = cameraMatrixColor.at<double>(1, 2);
    float *it;

    lookupY = cv::Mat(1, height, CV_32F);
    it = lookupY.ptr<float>();
    for(size_t r = 0; r < height; ++r, ++it)
    {
      *it = (r - cy) * fy;
    }

    lookupX = cv::Mat(1, width, CV_32F);
    it = lookupX.ptr<float>();
    for(size_t c = 0; c < width; ++c, ++it)
    {
      *it = (c - cx) * fx;
    }
  }

     const float badPoint = std::numeric_limits<float>::quiet_NaN();

    #pragma omp parallel for
    for(int r = 0; r < depth.rows; ++r)
    {
      pcl::PointXYZRGBA *itP = &cloud->points[r * depth.cols];
      const uint16_t *itD = depth.ptr<uint16_t>(r);
      const cv::Vec3b *itC = color.ptr<cv::Vec3b>(r);
      const float y = lookupY.at<float>(0, r);
      const float *itX = lookupX.ptr<float>();

      for(size_t c = 0; c < (size_t)depth.cols; ++c, ++itP, ++itD, ++itC, ++itX)
      {
        register const float depthValue = *itD / 1000.0f;
        // Check for invalid measurements
        if(isnan(depthValue) || depthValue <= 0.001)
        {
          // not valid
          itP->x = itP->y = itP->z = badPoint;
          itP->rgba = 0;
          continue;
        }
        itP->z = depthValue;
        itP->x = *itX * depthValue;
        itP->y = y * depthValue;
        itP->b = itC->val[0];
        itP->g = itC->val[1];
        itP->r = itC->val[2];
        itP->a = 255;
      }
    }
#endif

std::pair<cv::Mat,cv::Mat> preparemake3D(int w, int h, const Freenect2Device::IrCameraParams & depth_p)
{
	cv::Mat m1(w,1,CV_32FC1);
	cv::Mat m2(h,1,CV_32FC1);
	float * pm1 = (float*)m1.data;
	float * pm2 = (float*)m2.data;
	for(int i = 0; i < w; i++)
	{
		*pm1++ = (i-depth_p.cx+0.5)/depth_p.fx;
	}
	for (int i = 0; i < h; i++)
	{
		*pm2++ = (i-depth_p.cy+0.5)/depth_p.fy;
	}
	return {m1,m2};
}

int make3D(cv::Mat & out, cv::Mat & indepth, cv::Mat & incolor, std::pair<cv::Mat,cv::Mat> pp)
{
		int good = 0;
	std::cout << "make 3D with cut at distance\n";
	uint8_t * pc = (uint8_t *)incolor.data;
	float * pd = (float*)indepth.data;
	uint8_t * poi = (uint8_t*)out.data;
	float * pw = (float*)pp.first.data;
	float * ph = (float*)pp.second.data;
	for(int r = 0; r < indepth.rows; r++)
	{
		const float w = ph[r];
		for(int c = 0; c < indepth.cols; c++, pc+=3,pd++)
		{
			auto po = (float*)poi;
			float z = *pd;
			if(z <= 0 || z > 3000 || (pc[0] == 0 && pc[1] == 0 && pc[2] == 0))
			{
			}
			else
			{
				// xpix = (fx*xworld+cx*z)/z
				// xworld = (xpix*z-cx*z)/fx
				//
				// Apply 
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
			}

		}
	}
	std::cout << good << std::endl;
	return good;
}

int make3D(cv::Mat & out, cv::Mat & indepth, cv::Mat & incolor, const Freenect2Device::IrCameraParams & depth_p)
{
	int good = 0;
	std::cout << "make 3D with cut at distance\n";
	uint8_t * pc = (uint8_t *)incolor.data;
	float * pd = (float*)indepth.data;
	uint8_t * poi = (uint8_t*)out.data;
	for(int r = 0; r < indepth.rows; r++)
	{
		const float w = (r-depth_p.cy+0.5)/depth_p.fy;
		for(int c = 0; c < indepth.cols; c++, pc+=3,pd++)
		{
			auto po = (float*)poi;
			float z = *pd;
			if(z <= 0 || z > 3000 || (pc[0] == 0 && pc[1] == 0 && pc[2] == 0))
			{
			}
			else
			{
				// xpix = (fx*xworld+cx*z)/z
				// xworld = (xpix*z-cx*z)/fx
				//
				// Apply 
				auto poc = (uint8_t*)(po+3);
				const float rx = (c-depth_p.cx+0.5)*z/depth_p.fx;
				const float ry = w*z;
				po[0] = rx;
				po[1] = -ry;
				po[2] = z;
				poc[0] = pc[2];
				poc[1] = pc[1];
				poc[2] = pc[0];
				good++;
				poi += 3*4+3;
			}

		}
	}
	std::cout << good << std::endl;
	return good;
}

int make3D4(cv::Mat & out, cv::Mat & indepth, cv::Mat & incolor, const Freenect2Device::IrCameraParams & depth_p)
{
	int good = 0;
	std::cout << "make 3D with cut at distance\n";
	uint32_t * pc = (uint32_t *)incolor.data;
	float * pd = (float*)indepth.data;
	uint8_t * poi = (uint8_t*)out.data;
	for(int r = 0; r < indepth.rows; r++)
	{
		const float w = (r-depth_p.cy)/depth_p.fy;
		for(int c = 0; c < indepth.cols; c++, pc++,pd++)
		{
			auto po = (float*)poi;
			float z = *pd;
			if(z <= 0 || z > 3000 || (pc[0] == 0))
			{
			}
			else
			{
				// xpix = (fx*xworld+cx*z)/z
				// xworld = (xpix*z-cx*z)/fx
				//
				// Apply 
				auto poc = (uint32_t*)(po+3);
				const float rx = (c-depth_p.cx)*z/depth_p.fx;
				const float ry = w*z;
				po[0] = rx;
				po[1] = -ry;
				po[2] = z;
				poc[0] = pc[0];
				good++;
				poi += 3*4+4;
			}

		}
	}
	std::cout << good << std::endl;
	return good;
}

void saveply(const char * name, const cv::Mat & p3, int good, int item)
{
	std::ofstream onf(name,std::ios::binary);

	onf << "ply\nformat binary_little_endian 1.0\nelement vertex " << good << std::endl;
	onf << "property float x\nproperty float y\nproperty float z\n";
	onf << "property uchar red\nproperty uchar green\nproperty uchar blue\n";
	onf << "end_header" << std::endl;
	onf.write((const char*)p3.data,good*item);

}

inline std::streampos filesize(std::istream & inf)
{
    inf.seekg( 0, std::ios::end );
    std::streampos n = inf.tellg();
    inf.seekg( 0, std::ios::beg );
    return n;
}

void makepaths(std::string &d, std::string &c,std::string b, int fid, std::string & od)
{
	char buf[128];
	sprintf(buf,"%010d",fid);
	d = b + "Depth/frame_";
	d += buf;
	d += ".png";

	c = b + "Color/frame_";
	c += buf;
	c += ".jpg";

	od = b + "RDepth/frame_";
	od += buf;
	od += ".png";
}
int main(int argc, char * argv[])
{
	Freenect2Device::IrCameraParams depth_p;
	Freenect2Device::ColorCameraParams rgb_p;
	fillin(depth_p,rgb_p);
	Registration r(depth_p,rgb_p);
	// void apply(const Frame* rgb, const Frame* depth, Frame* undistorted, Frame* registered, const bool enable_filter = true, Frame* bigdepth = 0) const;
	std::array<int,2> rgbsize({1920,1080}),depthsize({512,424});
	FrameT<int32_t> colorin(rgbsize);
	FrameT<uint8_t> grayin(rgbsize);
	FrameT<float> depthin(depthsize);
	FrameT<float> undistorted(depthsize);
	FrameT<int32_t> registeredgray(depthsize);
	FrameT<uint8_t> registered(depthsize);
	FrameT<rgb_t> registered3(depthsize);
	FrameT<rgb_t> colorin3(rgbsize);
	FrameT<float> bigdepth(r.getbigfiltermapsize(),1);
	FrameT<uint16_t> bigdepth16(rgbsize);


	// load depth 16bit => float
	// load color as RGBA
	const char * base = "/Users/eruffaldi/Documents/RAMCIP_CERTH_Foot_Subject2/Subject_5/SHOE_ON/FRONT_RIGHT_LIFT/";
	for(int fid = 180; fid <= 280; fid++)
	{
		// frame_0000000181
		std::string fdepth,fcolor,fodepth;
		makepaths(fdepth,fcolor,base,fid,fodepth);
		std::cout << fdepth << " " << fcolor << std::endl;

		auto dump = [] (const cv::Mat & x, const char * cp) {
			std::cout << cp << " " << x.rows << " " << x.cols << " elemsize:" << x.elemSize() << " channels " << x.channels() << " flags " << x.flags << " data " << (void*)x.data << std::endl;
		};
		Timer tloadj;
		cv::Mat micolor = cv::imread(fcolor.c_str(),CV_LOAD_IMAGE_COLOR);
		if(micolor.rows == 0)
			continue;
		dump(micolor,"micolor");
		tloadj.stop();
		Timer tloadt;
		{
			std::ifstream inf(fcolor.c_str(),std::ios::binary);
			if(!inf)
				continue;
			int n = filesize(inf);
			std::vector<uint8_t> data(n);
			inf.read((char*)&data[0],n);
			std::cout << "loaded file as " << n << std::endl;

			decodejpeg(&data[0],data.size(),1920,1080,micolor.data,TJPF_BGR);
		}
		tloadt.stop();

		Timer tloadt1;
		cv::Mat micolorg(depthsize[1], depthsize[0], CV_8UC1, grayin.data);
		{
			std::ifstream inf(fcolor.c_str(),std::ios::binary);
			int n = filesize(inf);
			std::vector<uint8_t> data(n);
			inf.read((char*)&data[0],n);
			std::cout << "gray loaded file as " << n << std::endl;

			decodejpeg(&data[0],data.size(),1920,1080,micolorg.data,TJPF_GRAY);
		}
		tloadt1.stop();

		Timer tloadd;
		cv::Mat midepth = cv::imread(fdepth.c_str(),CV_LOAD_IMAGE_UNCHANGED);
		tloadd.stop();
		cv::Mat mcolor=micolor,mdepth=midepth;
	//	cv::flip(micolor,mcolor,0);
	//	cv::flip(midepth,mdepth,0);

		Timer trest;
		cv::Mat mdepthf(depthsize[1], depthsize[0], CV_32FC1, depthin.data);
		cv::Mat mcolor3(rgbsize[1], rgbsize[0], CV_8UC3, colorin3.data);
		cv::Mat mcolor4(rgbsize[1], rgbsize[0], CV_8UC4, colorin.data);
		cv::Mat mcolorout(depthsize[1], depthsize[0], CV_8UC4, registered.data);
		cv::Mat mcolorout3(depthsize[1], depthsize[0], CV_8UC3, registered3.data);
		cv::Mat mundout(depthsize[1], depthsize[0], CV_32FC1, undistorted.data);
		cv::Mat mout3d(depthsize[1],depthsize[0]*(3*4+3),CV_8UC1);
		cv::Mat mbigdepth(rgbsize[1],rgbsize[0],CV_32FC1,bigdepth.data);

		dump(mcolor,"mcolor");
		dump(mcolor4,"mcolor4");
		dump(mdepth,"mdepth");
		dump(mdepthf,"mdepthf");
		dump(mcolorout,"mcolorout");
		

		{
			double min;
			double max;
			cv::minMaxIdx(mdepth, &min, &max);
			cv::Mat adjMap;
			cv::convertScaleAbs(mdepth, adjMap, 255 / max);
			//cv::imshow("Out", adjMap);
			std::cout << "Input Depth Color is min:max" << min << " " << max << " (mm)"<< std::endl;
		//	cv::waitKey();
		}

		// RGB to RGBA (can we do better?)
		int from_to[] = { 0,0, 1,1, 2,2};
		cv::mixChannels(&mcolor, 1, &mcolor4, 1, from_to, 3);

		mdepth.convertTo(mdepthf, CV_32FC1); // mm
		
		{
				double min;
				double max;
				cv::Mat adjMap;
				cv::minMaxIdx(mdepthf, &min, &max);
			//	cv::convertScaleAbs(mdepthf, adjMap, 255 / max);
			//	cv::imshow("Out", adjMap);

				std::cout << "Converted Depth Color is min:max" << min << " " << max << " (mm)"<< std::endl;
			}

		//cv::imshow("color",mcolor4);
		//cv::imshow("depth",mdepthf);
		//cv::waitKey();

		std::cout << "registering\n";
		mcolor.copyTo(mcolor3);

		Timer tapp1;
			if(!r.apply1(&grayin,&depthin,&undistorted,&registeredgray,true,&bigdepth))
			{
				std::cout<<"apply1 fail\n";
			}
		tapp1.stop();

		// bigdepth  => save PNG
		for(int x = 0; x < rgbsize[0]; x++)
			for(int y = 0; y < rgbsize[1]; y++)
			{
				bigdepth16.data_[y*rgbsize[0]+x] = htons((uint16_t)(bigdepth.data_[(y+1)*rgbsize[0]+x]));
			}
			std::cout << "saving " << fodepth << std::endl;
		lodepng_encode_file(fodepth.c_str(),(const uint8_t*)&bigdepth16.data_[0],rgbsize[0],rgbsize[1],LCT_GREY,16);
#if 0
		Timer tapp4;
		if(!r.apply4(&colorin,&depthin,&undistorted,&registered,true,&bigdepth))
			{
				std::cout<<"apply4 fail\n";
			}
		tapp4.stop();

		trest.stop();
		Timer tapp3;
		if(!r.apply3(&colorin3,&depthin,&undistorted,&registered3,true,&bigdepth))
		{
			std::cout << "apply3 failed\n";
		}
		else
		{
			tapp3.stop();
			std::cout << "registered\n";
			//cv::imshow("colorout",mcolorout3);
			//cv::imshow("undi",mundout);
			//cv::waitKey();
		}
#endif
	}

	// TODO: unprojection of the point to 3D using the depth parameters and 
	//
	// x = *map_x * depth_x + color_cy
	// 
	// z = same z
	return 0;
}