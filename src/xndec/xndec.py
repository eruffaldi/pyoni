

import ctypes,os

# XnStatus XnStreamUncompressDepth16ZWithEmbTable(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt16* pOutput, XnUInt32* pnOutputSize)
# XnStatus XnStreamUncompressDepth16Z(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt16* pOutput, XnUInt32* pnOutputSize)
# XnStatus XnStreamUncompressImage8Z(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)
# XnStatus XnStreamUncompressConf4(const XnUInt8* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize)

types = ["",".so",".dylib",".pyd"]
x = None
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

for a in types:
	try:
		x = ctypes.CDLL(os.path.join(dir_path,"libxndec" + a))
		break
	except:
		pass
f = x.XnStreamUncompressDepth16ZWithEmbTable
et = ctypes.POINTER(ctypes.c_uint8)
f.argtypes = [ctypes.c_char_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint16),ctypes.POINTER(ctypes.c_int)]
f.restype = ctypes.c_int
XnStreamUncompressDepth16ZWithEmbTable = f

f = x.XnStreamUncompressDepth16Z
et = ctypes.POINTER(ctypes.c_uint8)
f.argtypes = [ctypes.c_char_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint16),ctypes.POINTER(ctypes.c_int)]
f.restype = ctypes.c_int
XnStreamUncompressDepth16Z = f

f = x.XnStreamUncompressImage8Z
et = ctypes.POINTER(ctypes.c_uint8)
f.argtypes = [ctypes.c_char_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_int)]
f.restype = ctypes.c_int
XnStreamUncompressImage8Z = f

f = x.XnStreamUncompressConf4
et = ctypes.POINTER(ctypes.c_uint8)
f.argtypes = [ctypes.c_char_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_int)]
f.restype = ctypes.c_int
XnStreamUncompressConf4 = f

#XnStatus XnStreamCompressDepth16ZWithEmbTable(const XnUInt16* pInput, const XnUInt32 nInputSize, XnUInt8* pOutput, XnUInt32* pnOutputSize, XnUInt16 nMaxValue)
f = x.XnStreamCompressDepth16ZWithEmbTable
et = ctypes.POINTER(ctypes.c_uint8)
f.argtypes = [ctypes.POINTER(ctypes.c_uint16),ctypes.c_int,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_int),ctypes.c_int]
f.restype = ctypes.c_int
XnStreamCompressDepth16ZWithEmbTable = f


def allocoutput16(n):
	#pt = ctypes.c_uint16*n
	#p = pt()
	#return p
	return ctypes.create_string_buffer(n*2)

def allocoutput8(n):
	#pt = ctypes.c_uint16*n
	#p = pt()
	#return p
	return ctypes.create_string_buffer(n)

def doXnStreamUncompressConf4(input,outputbuffer):
	r = ctypes.c_int(len(outputbuffer));
	rr = XnStreamUncompressConf4(ctypes.c_char_p(input),len(input),ctypes.cast(outputbuffer,ctypes.POINTER(ctypes.c_uint8)),ctypes.byref(r))
	return (rr,r.value)

def doXnStreamUncompressImage8Z(input,outputbuffer):
	r = ctypes.c_int(len(outputbuffer));
	rr = XnStreamUncompressImage8Z(ctypes.c_char_p(input),len(input),ctypes.cast(outputbuffer,ctypes.POINTER(ctypes.c_uint8)),ctypes.byref(r))
	return (rr,r.value)

def doXnStreamUncompressDepth16ZWithEmbTable(input,outputbuffer):
	r = ctypes.c_int(len(outputbuffer));
	rr = XnStreamUncompressDepth16ZWithEmbTable(ctypes.c_char_p(input),len(input),ctypes.cast(outputbuffer,ctypes.POINTER(ctypes.c_uint16)),ctypes.byref(r))
	return (rr,r.value)

def doXnStreamCompressDepth16ZWithEmbTable(input,outputbuffer,maxvalue):
	r = ctypes.c_int(len(outputbuffer));
	rr = XnStreamCompressDepth16ZWithEmbTable(ctypes.cast(input,ctypes.POINTER(ctypes.c_uint16)),len(input),ctypes.cast(outputbuffer,ctypes.POINTER(ctypes.c_uint8)),ctypes.byref(r),maxvalue)
	return (rr,r.value)


def doXnStreamUncompressDepth16Z(input,outputbuffer):
	r = ctypes.c_int(len(outputbuffer));
	rr = XnStreamUncompressDepth16Z(ctypes.c_char_p(input),len(input),ctypes.cast(outputbuffer,ctypes.POINTER(ctypes.c_uint16)),ctypes.byref(r))
	return (rr,r.value)


if __name__ == "__main__":

	a = "1234"
	b = allocoutput16(123)
	print doXnStreamUncompressDepth16ZWithEmbTable(a,b)