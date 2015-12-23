/*
 * world = K [R | t]
 */
#include <Eigen/Dense>
#include <iostream>
#include <math.h>

struct rgbpoint
{
	rgbpoint(): r(0),g(0),b(0) {}
	char r,g,b;
} __attribute__((packed));

// [sx 0 cx]
// [0 sy cy]
// [0 0 1]
//
// to 4x4
void intrinsics2m44(Eigen::Matrix4d & out, Eigen::Matrix3d & in)
{
	out.setZero();
	out.block<3,3>(0,0) = in;
	out(3,3) = 1;

//	out << in(0,0),in(0,1),0,in(0,2)    ,in(1,0),in(1,1),0,in (1,2),   0,0,1,0,   0,0,0,1;
}

void composerotot(Eigen::Matrix4d& out, const Eigen::Matrix3d & R, const Eigen::Vector3d & T)
{
		out.setZero();
		out.block<3,3>(0,0) = R;
		out.block<3,1>(0,3) = T;
		out(3,3) = 1;

}

#ifdef __MINGW32__
#define DE __declspec(dllexport)
#else
#define DE

#endif

extern "C"
{
	void DE initlibanyregistration(){}
	/// output is color computed as depth in sizes 
	void DE register2color(char * outrgb, int cw, int ch, const char * rgb, int dw, int dh, const uint16_t * depth, const double depthK[9], const double colorK[9], const double inrotation[9], const double position[3])
	{	
		static_assert(sizeof(rgbpoint) == 3,"rgpoint should be 3 bytes");

		float maxdistance_mm = 10000;


		Eigen::Matrix3d rotation = Eigen::Matrix<double, 3, 3, Eigen::RowMajor>::Map(inrotation);
		Eigen::Vector3d translation = Eigen::Vector3d::Map(position);
		Eigen::Matrix3d depth_matrix = Eigen::Matrix<double, 3, 3, Eigen::RowMajor>::Map(depthK);
		Eigen::Matrix3d rgb_matrix = Eigen::Matrix<double, 3, 3, Eigen::RowMajor>::Map(colorK);

		std::cout << "Rotation is\n " << rotation << std::endl;
		std::cout << "Kdepth is\n" << depth_matrix << std::endl;

		Eigen::Matrix4d rototranslationD2R;
		Eigen::Matrix4d odepth_matrix;
		Eigen::Matrix4d orgb_matrix;
		
		intrinsics2m44(odepth_matrix,depth_matrix);
		intrinsics2m44(orgb_matrix,rgb_matrix);
		composerotot(rototranslationD2R,rotation,translation);

		std::cout << "Kdepth4 is\n" << odepth_matrix << std::endl;

		std::cout << "rototraslation(W->D)\n" << rototranslationD2R << std::endl;

		Eigen::Matrix4d depth2rgb4 = orgb_matrix * rototranslationD2R * odepth_matrix.inverse();
//		Eigen::Matrix4d depth2rgb4 = orgb_matrix * (odepth_matrix*rototranslationD2R).inverse();

		std::cout << "depth2rgb4\n" << depth2rgb4 << std::endl;

		const  uint16_t * inputdepth_mm = depth;
		rgbpoint * out = (rgbpoint*)outrgb;
		const rgbpoint * inputcolor = (rgbpoint*)rgb;

		memset(out,0,dw*dh*3);

		for(int y = 0; y < dh; ++y)
		{	
			for(size_t x = 0; x < dw; ++x, inputdepth_mm++,out++)
			{
				if(!*inputdepth_mm)
					continue;

				// Check for invalid measurements
				if(*inputdepth_mm >= maxdistance_mm)
					continue;

				const float depth_value = *inputdepth_mm / 1000.0f;


				//Eigen::Vector4d psd(x, y, 1.0, 1.0/depth_value);
				//Eigen::Vector4d psddiv = psd * depth_value;
				//Eigen::Vector4d pworld = depth2world * psddiv;
				//Eigen::Vector4d rgb_img_homo = world2rgb * pworld;

				Eigen::Vector4d psd(x, y, 1.0, 1.0/depth_value);
				Eigen::Vector4d rgb_img_homo = depth2rgb4 * (psd * depth_value);
				Eigen::Vector4d rgb_img = rgb_img_homo / rgb_img_homo.z();


				int ix = rgb_img.x();
				int iy = rgb_img.y();

				if(ix >= 0 && ix < cw && iy >= 0 && iy < ch)
				{	
					*out = inputcolor[iy*cw+ix];
				}
			}
		}
	}

	// NOT WORKING DUE TO FILLING
	/// output is depth computed as color in size
	void DE register2depth(uint16_t * outdepth, int cw, int ch, const char * rgb, int dw, int dh, const uint16_t * depth, const double depthK[9], const double colorK[9], const double inrotation[9], const double position[3])
	{	
		float maxdistance = 10;

		Eigen::Matrix3d rotation = Eigen::Matrix<double, 3, 3, Eigen::RowMajor>::Map(inrotation);
		Eigen::Vector3d translation = Eigen::Vector3d::Map(position);
		Eigen::Matrix3d depth_matrix = Eigen::Matrix<double, 3, 3, Eigen::RowMajor>::Map(depthK);
		Eigen::Matrix3d rgb_matrix = Eigen::Matrix<double, 3, 3, Eigen::RowMajor>::Map(colorK);

		Eigen::Matrix4d rototranslationD2R;
		Eigen::Matrix4d orgb_matrix,odepth_matrix;

		intrinsics2m44(odepth_matrix,depth_matrix);
		intrinsics2m44(orgb_matrix,rgb_matrix);
		composerotot(rototranslationD2R,rotation,-translation);


		//odepth_matrix.block<3,3>(0,0) = depth_matrix;
		//odepth_matrix(3,3) = 1;

		//orgb_matrix.block<3,3>(0,0) = rgb_matrix;
		//orgb_matrix(3,3) = 1;

		std::cout << rototranslationD2R << std::endl;

		Eigen::Matrix4d depth2rgb4 = orgb_matrix * rototranslationD2R * odepth_matrix.inverse();
		Eigen::Matrix3d rgb2depth = depth2rgb4.block<3,3>(0,0).inverse();


		memset(outdepth,0,cw*ch*2); // cleanup output (max value)
		auto po = outdepth;

		for(int y = 0; y < ch; ++y)
		{	
			for(size_t x = 0; x < cw; ++x,++po)
			{

				Eigen::Vector3d rgb_i(x,y,1); // 2D homo
				Eigen::Vector3d depth_sub_i = rgb2depth * rgb_i; // to 2D homo
				int ix = depth_sub_i.x();
				int iy = depth_sub_i.y();

				// if inside, and valid and nearer than the current
				if(ix >= 0 && ix  < dw && iy >= 0 && iy < dh )
				{
					 int off = iy*dw+ix;
					 uint16_t current = depth[off];
					 *po = current;
					 //uint16_t *target = outdepth + off; // target output
					 //if(current > 0 && (*target == 0 || *target > current))
					 //*target = current;
				}

				/*
					To obtain world coords
					Eigen::Vector4d psd(depth_sub_i.x(),depth_sub_i.y(), 1.0, 1.0/newdepth);
					Eigen::Vector4d psddiv = psd * newdepth; // (x*newdepth,y*newdepth,newdepth,1)
					Eigen::Vector4d pworld =  depth2world  * psddiv;
				*/
			}
		}
	}
}