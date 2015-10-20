#include <iostream>
#include <vector>
#include "registrationK2.h"
#include <array>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include <fstream>


using namespace libfreenect2;


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

int make3D(cv::Mat & out, cv::Mat & indepth, cv::Mat & incolor, const Freenect2Device::IrCameraParams & depth_p)
{
	int good = 0;
	std::cout << "make 3D with cut at distance\n";
	uint8_t * pc = (uint8_t *)incolor.data;
	float * pd = (float*)indepth.data;
	uint8_t * poi = (uint8_t*)out.data;
	for(int r = 0; r < indepth.rows; r++)
	{
		for(int c = 0; c < indepth.cols; c++, pc+=3,pd++)
		{
			auto po = (float*)poi;
			float z = *pd;
			if(z <= 0 || z > 3000)
			{
			}
			else
			{
				// xpix = (fx*xworld+cx*z)/z
				// xworld = (xpix*z-cx*z)/fx
				const float rx = (c-depth_p.cx)*z/depth_p.fx;
				const float ry = (r-depth_p.cy)*z/depth_p.fy;
				po[0] = rx;
				po[1] = ry;
				po[2] = z;
				auto poc = (uint8_t*)(po+3);
				poc[0] = pc[2];
				poc[1] = pc[1];
				poc[2] = pc[0];
				good++;
				poi += 3*4+3;
			}

		}
	}
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

void makepaths(std::string &d, std::string &c,std::string b, int fid)
{
	char buf[128];
	sprintf(buf,"%010d",fid);
	d = b + "Depth/frame_";
	d += buf;
	d += ".png";

	c = b + "Color/frame_";
	c += buf;
	c += ".jpg";
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
	FrameT<float> depthin(depthsize);
	FrameT<float> undistorted(depthsize);
	FrameT<int32_t> registered(depthsize);
	FrameT<rgb_t> registered3(depthsize);
	FrameT<rgb_t> colorin3(rgbsize);
	FrameT<float> bigdepth(r.getbigfiltermapsize(),1);


	// load depth 16bit => float
	// load color as RGBA
	const char * base = "/Users/eruffaldi/RAMCIP_CERTH_Foot_Subject2/Subject_5/SHOE_ON/FRONT_RIGHT_LIFT/";
	int fid = 180;
	// frame_0000000181
	std::string fdepth,fcolor;
	makepaths(fdepth,fcolor,base,fid);
	std::cout << fdepth << " " << fcolor << std::endl;

	cv::Mat mcolor = cv::imread(fcolor.c_str(),CV_LOAD_IMAGE_COLOR);
	cv::Mat mdepth = cv::imread(fdepth.c_str(),CV_LOAD_IMAGE_UNCHANGED);

	cv::Mat mdepthf(depthsize[1], depthsize[0], CV_32FC1, depthin.data);
	cv::Mat mcolor3(rgbsize[1], rgbsize[0], CV_8UC3, colorin3.data);
	cv::Mat mcolor4(rgbsize[1], rgbsize[0], CV_8UC4, colorin.data);
	cv::Mat mcolorout(depthsize[1], depthsize[0], CV_8UC4, registered.data);
	cv::Mat mcolorout3(depthsize[1], depthsize[0], CV_8UC3, registered3.data);
	cv::Mat mundout(depthsize[1], depthsize[0], CV_32FC1, undistorted.data);
	cv::Mat mout3d(depthsize[1],depthsize[0]*(3*4+3),CV_8UC1);

	auto dump = [] (const cv::Mat & x, const char * cp) {
		std::cout << cp << " " << x.rows << " " << x.cols << " elemsize:" << x.elemSize() << " channels " << x.channels() << " flags " << x.flags << " data " << (void*)x.data << std::endl;
	};
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
//	if(!r.apply(&colorin,&depthin,&undistorted,&registered,true,&bigdepth))
	if(!r.apply3(&colorin3,&depthin,&undistorted,&registered3,true,&bigdepth))
	{
		std::cout << "reg failed\n";
	}
	else
	{
		std::cout << "registered\n";
		cv::imshow("colorout",mcolorout3);
		//cv::imshow("undi",mundout);
		//cv::waitKey();
	}
	int good = make3D(mout3d,mundout,mcolorout3,depth_p);
	saveply("x.ply",mout3d,good,(3*4+3));

	// TODO: unprojection of the point to 3D using the depth parameters and 
	//
	// x = *map_x * depth_x + color_cy
	// 
	// z = same z
	return 0;
}