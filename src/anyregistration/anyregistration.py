
import ctypes,sys,png,array,os
from PIL import Image

#	void register2color(char * outrgb, int cw, int ch, const char * rgb, int dw, int dh, const uint16_t * depth, const double depthK[9], const double colorK[9], const double inrotation[9], const double position[3])
#	void register2depth(uint16_t * outdepth, int cw, int ch, const char * rgb, int dw, int dh, const uint16_t * depth, const double depthK[9], const double colorK[9], const double inrotation[9], const double position[3])

p8 = ctypes.POINTER(ctypes.c_uint8) # for rgb
p16 = ctypes.POINTER(ctypes.c_uint16) # for depth
pd = ctypes.POINTER(ctypes.c_double) # generic
ad3 = ctypes.c_double * 3  # for pos
ad5 = ctypes.c_double * 5  # for dist
ad9 = ctypes.c_double * 9  # for intrinsics
ad16 = ctypes.c_double * 16 # for affine

ci = ctypes.c_int;

types = ["",".so",".dylib",".pyd"]
x = None
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

for a in types:
	try:
		x = ctypes.CDLL(os.path.join(dir_path,"libanyregistration" + a))
		break
	except:
		pass

f = x.register2color
f.argtypes = [p8,ci,ci,p8,ci,ci,p16,ad9,ad9,ad9,ad3]
register2color = f

f = x.register2depth
f.argtypes = [p16,ci,ci,p8,ci,ci,p16,ad9,ad9,ad9,ad3]
register2depth = f

def depth2color(x):
	c = min(255,int(x*255.0/2000.0))
	if c != 0:
		c = 255-c;
	return (c,c,0)

def blend(p,i,c):
	a = 0.7
	b = 0.3
	p[i*3] = int(p[i*3]*a + c[0]*b)
	p[i*3+1] = int(p[i*3+1]*a  + c[1]*b)
	p[i*3+2] = int(p[i*3+2]*a + c[2]*b)


def image2buffer(name):
	# http://pillow.readthedocs.org/en/latest/reference/Image.html
	inc_i = Image.open(name)
	inc = inc_i.tostring() #Image.tobytes(inc_i,encoder_name='raw')
	return inc

def buffer2image(buffer,size):
	return Image.frombytes("RGB", size, buffer, decoder_name='raw')

def saveimage(image,name,t="JPEG"):
	print "saving image",image
	image.save(name,t)

def savedepthpng(buffer,size,name):
	xres,yres = size
	w = png.Writer(width=size[0],height=size[1],greyscale=True,bitdepth=16)
	aa = array.array("H")
	aa.fromstring(buffer)
	print "saving",size,"of",len(aa)
	w.write(open(name,"wb"),[aa[i*xres:(i+1)*xres] for i in range(0,yres)])	

def savedepthpngcolor(buffer,size,name):
	xres,yres = size
	w = png.Writer(width=size[0],height=size[1],greyscale=True,bitdepth=8)
	aa = array.array("H")
	aa.fromstring(buffer)
	print "saving",size,"of",len(aa)
	rows = [aa[i*xres:(i+1)*xres] for i in range(0,yres)]
	w.write(open(name,"wb"),[[min(int(x*255.0/8000.0),255) for x in y] for y in rows])

def depthpng2buffer(name):
	# load png filename grayscale 16 bit
	p = png.Reader(open(name,"rb"))
	w,h,pi,me = p.read_flat()
	print "read ",w,h,len(pi),me
	return pi

def savedepth(buffer,name):
	open(name,"wb").write(buffer)

def mergedepthcolor(d,c):
	ad = array.array("H")
	ad.fromstring(d)
	aa = array.array("B")
	aa.fromstring(c)
	for i in range(0,len(ad)):
		x = ad[i]
		blend(aa,i,depth2color(ad[i]))
	return aa.tostring()

def doregister2color(outc,depthin,colorin,sizergb,Drgb,Krgb,sizedepth,Ddepth,Kdepth,R,T):
	if outc is None:
		outc = ctypes.create_string_buffer(sizedepth[0]*sizedepth[1]*3)
	poutc = ctypes.cast(outc,p8)
	prgb = ctypes.cast(ctypes.c_char_p(colorin),p8)
	if isinstance(depthin,array.array):
		print "input is array"
		addr, count = depthin.buffer_info()
		pdepth = ctypes.cast(addr, p16)
	else:
		pdepth = ctypes.cast(depthin,p16)
	pKdepth = ad9(*Kdepth)
	pDdepth = ad5(*Ddepth)
	pKrgb = ad9(*Krgb)
	pDrgb = ad5(*Drgb)
	pR = ad9(*R)
	pT = ad3(*T)
	register2color(poutc,sizergb[0],sizergb[1],prgb,sizedepth[0],sizedepth[1],pdepth,pKdepth,pKrgb,pR,pT)
	return outc

def doregister2depth(outd,depthin,colorin,sizergb,Drgb,Krgb,sizedepth,Ddepth,Kdepth,R,T):
	if outd is None:
		outd = ctypes.create_string_buffer(sizergb[0]*sizergb[1]*2)
	#outd = (ctypes.c_ushort * (sizedepth[0]*sizedepth[1]))()
	poutd = ctypes.cast(outd,p16)
	prgb = ctypes.cast(ctypes.c_char_p(colorin),p8)
	if isinstance(depthin,array.array):
		addr, count = depthin.buffer_info()
		pdepth = ctypes.cast(addr, p16)
	else:
		pdepth = ctypes.cast(ctypes.c_char_p(depthin),p16)
	pKdepth = ad9(*Kdepth)
	pDdepth = ad5(*Ddepth)
	pKrgb = ad9(*Krgb)
	pDrgb = ad5(*Drgb)
	pR = ad9(*R)
	pT = ad3(*T)
	print ctypes.addressof(poutd.contents)
	register2depth(poutd,sizergb[0],sizergb[1],prgb,sizedepth[0],sizedepth[1],pdepth,pKdepth,pKrgb,pR,pT)
	return outd

#TODO merge the merged images and output ad jpeg or png to show alignment

if __name__ == '__main__':

	# Asus xtion, distortion is unused
	size = (640,480)
	Drgb = (0.041623, -0.105707, -0.001538, 0.000755, 0.0)
	Ddepth = (0.041623, -0.105707, -0.001538, 0.000755, 0.0)

	Krgb = (533.9089, 0.0, 321.09951,    0.0, 534.555793, 237.786129,    0.0, 0.0, 1.0)
	Kdepth = (570, 0.0, 320,   0.0, 570, 240,    0.0, 0.0, 1.0)


	#http://qianyi.info/scenedata.html

	#http://robotics.dei.unipd.it/images/Papers/Conferences/basso2014unsupervised.pdf
	q= (0.999983,-0.00337542, 0.00425487,0.00190883)
	R = (1,0,0,  0,1,0, 0,0,1)
	T = (0.0222252,0,0)
	#export A=/Users/eruffaldi/Desktop/scotachtura2.oni
	#./pyonitool.py --extractdepth out --fseek 0 --fduration 1 $A
	#./pyonitool.py --extractcolor out --fseek 0 --fduration 1 $A

	if len(sys.argv) == 3:
		indepth = sys.argv[1]
		incolor = sys.argv[2]
	else:
		indepth = "depth.png"
		incolor = "color.jpg"
	if indepth.endswith(".png"):
		ind = depthpng2buffer(indepth) # note that pillow does not sypport 16bit
	else:
		ind = open(indepth,"rb").read()
	inc = image2buffer(incolor)

	outc = doregister2color(None,ind,inc,size,Drgb,Krgb,size,Ddepth,Kdepth,R,T)
	outd = doregister2depth(None,ind,inc,size,Drgb,Krgb,size,Ddepth,Kdepth,R,T)

	if indepth.endswith(".png"):
		savedepthpng(outd.raw,size,"outdepth16.png")
		savedepthpngcolor(outd.raw,size,"outdepthc.png")
	else:
		savedepth(outd.raw,"outdepth.bin")

	outci = buffer2image(outc.raw,size)
	saveimage(outci,"outimage.jpg")

	outci = buffer2image(mergedepthcolor(ind,inc),size)
	saveimage(outci,"mergeinput.jpg")

	outci = buffer2image(mergedepthcolor(ind,outc),size)
	saveimage(outci,"mergenewcolor.jpg")

	outci = buffer2image(mergedepthcolor(outd,inc),size)
	saveimage(outci,"mergenewdepth.jpg")

	# merge the images: inputdepth+adjustedcolor OR inputcolor+adjusteddepth
