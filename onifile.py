import struct

RECORD_END = 0x0B
HEADER_MAGIC_SIZE = 4
MAGIC = 0x0052494E
MAGICS = "NIR\0"
RHMAGIC = "NI10"
HEADER_SIZE = 4*5+8

def XN_CODEC_ID(c1, c2, c3, c4):
    c1 = ord(c1)
    c2 = ord(c2)
    c3 = ord(c3)
    c4 = ord(c4)
    return ((c4 << 24) | (c3 << 16) | (c2 << 8) | c1)

def parseindex(a):
    ts = parseint64(a)
    cid = parseint(a)
    pos = parseint64(a)
    return dict(timestamp=ts,config=cid,offset=pos)

def makeindex(a):
    return struct.pack("=qiq",a["timestamp"],a["config"],a["offset"])

#BAD
NODE_TYPE_DEVICE = 1
NODE_TYPE_DEPTH = 2
NODE_TYPE_IMAGE= 3
NODE_TYPE_IR = 4

XN_CODEC_UNCOMPRESSED =XN_CODEC_ID('N','O','N','E')
XN_CODEC_16Z = XN_CODEC_ID('1','6','z','P')
XN_CODEC_16Z_EMB_TABLES =XN_CODEC_ID('1','6','z','T')
XN_CODEC_8Z =XN_CODEC_ID('I','m','8','z')
XN_CODEC_JPEG =XN_CODEC_ID('J','P','E','G')


ONI_PIXEL_FORMAT_DEPTH_1_MM = 100
ONI_PIXEL_FORMAT_DEPTH_100_UM = 101
ONI_PIXEL_FORMAT_SHIFT_9_2 = 102
ONI_PIXEL_FORMAT_SHIFT_9_3 = 103

ONI_PIXEL_FORMAT_RGB888 = 200
ONI_PIXEL_FORMAT_YUV422 = 201
ONI_PIXEL_FORMAT_GRAY8 = 202
ONI_PIXEL_FORMAT_GRAY16 = 203
ONI_PIXEL_FORMAT_JPEG = 204
ONI_PIXEL_FORMAT_YUYV = 205

RECORD_NODE_ADDED_1_0_0_4       = 0x02
RECORD_INT_PROPERTY             = 0x03
RECORD_REAL_PROPERTY            = 0x04
RECORD_STRING_PROPERTY          = 0x05
RECORD_GENERAL_PROPERTY         = 0x06
RECORD_NODE_REMOVED             = 0x07
RECORD_NODE_DATA_BEGIN          = 0x08
RECORD_NODE_STATE_READY         = 0x09
RECORD_NEW_DATA                 = 0x0A
RECORD_END                      = 0x0B
RECORD_NODE_ADDED_1_0_0_5       = 0x0C
RECORD_NODE_ADDED               = 0x0D
RECORD_SEEK_TABLE               = 0x0E

"""
struct FileHeaderData
{
    XnUInt8 identity[IDENTITY_SIZE];
    struct Version
    {
        XnUInt8 major;
        XnUInt8 minor;
        XnUInt16 maintenance;
        XnUInt32 build;
    } version;
    XnUInt64 maxTimeStamp;
    XnUInt32 maxNodeId;
};
struct RecordHeaderData
{
    XnUInt32 magic;
    XnUInt32 recordType;
    XnUInt32 nodeId;
    XnUInt32 fieldsSize; // comprises the HEADER_SIZE
    XnUInt32 payloadSize;
    XnUInt64 undoRecordPos;
};

Version structure:
	XnUInt8         nMajor
	XnUInt8         nMinor
	XnUInt16        nMaintenance
	XnUInt32        nBuild
"""

#emitCommonHeader(RECORD_NODE_STATE_READY, nodeId, /*undoRecordPos*/ 0);

#emit_RECORD_NODE_DATA_BEGIN
#   framecount 4
#   maxts 8

#emit_RECORD_NEW_DATA
#   timestamp 8
#    Seek table position


def parseint(a):
    return struct.unpack("i",a.read(4))[0]

def parseint64(a):
    return struct.unpack("q",a.read(8))[0]

def makeint64(a):
    return struct.pack("q",a)

def parsedata(a,h):
    a.seek(h["poffset"],0)
    ts =    parseint64(a)
    seek  = parseint(a)
    return dict(timestamp=ts,dataoffset=seek)

def patchtime(a,h,ot):
    a.seek(h["poffset"],0)
    a.write(makeint64(ot))

def parsestr(a):
    namelen = parseint(a)
    name = a.read(namelen)[0:-1]
    return name

def writeseek(a,h):
    print "writing",len(h["data"])
    a.seek(h["poffset"],0)
    for x in h["data"]:
        y = makeindex(x)
        a.write(y)

def parseseek(a,h):
    a.seek(h["poffset"],0)
    r = []
    n = h["ps"]/(8+8+4)
    print "reading seektable",n
    for i in range(0,n):
        t = parseindex(a)
        r.append(t)
    h["data"] = r
    return h
def makestr(a,s):
    return struct.pack("=i",len(s)+1)+ s+"\x00" 

codec2id = dict(raw=XN_CODEC_UNCOMPRESSED,jpeg=XN_CODEC_JPEG)
codec2id["16z"] = XN_CODEC_16Z
codec2id["8z"] = XN_CODEC_8Z
codec2id["16zt"] = XN_CODEC_16Z_EMB_TABLES

def patchadded(a,h,hh):
    a.seek(h["poffset"],0)
    a.write(makestr(a,hh["name"]))
    #print "codecback",codec2id.get(hh["codec"],hh["codec"])
    ocodec = codec2id.get(hh["codec"],hh["codec"])
    a.write(struct.pack("=iiiqq",hh["nodetype"],ocodec,hh["frames"],hh["mints"],hh["maxts"]))
def parseadded(a,h):
    a.seek(h["poffset"],0)
    name = parsestr(a)
    nodetype = parseint(a)
    codec = parseint(a)
    nframes = parseint(a)
    mints = parseint64(a)
    maxts = parseint64(a)
    ocodec = codec
    if codec == XN_CODEC_UNCOMPRESSED:
        codec = "raw"
    elif codec == XN_CODEC_16Z:
         codec = "16z"
    elif codec == XN_CODEC_16Z_EMB_TABLES:
        codec = "16zt"
    elif codec == XN_CODEC_8Z:
        codec = "8z"
    elif codec == XN_CODEC_JPEG:
        codec = "jpeg"
    #print "codecin",codec,ocodec
    return dict(name=name,nodetype=nodetype,codec=codec,frames=nframes,mints=mints,maxts=maxts)

def parseprop(a,h):
    a.seek(h["poffset"],0)
    name = parsestr(a)
    datalen = parseint(a)-4
    data = a.read(datalen)
    if h["rt"] == RECORD_INT_PROPERTY:
        data = struct.unpack("i",data)[0]    
    return dict(name=name,data=data)

    


def writehead1(a,h):
    """writes a new header"""
    version = struct.pack("bbhi",*h["version"])
    ts = struct.pack("q",h["ts"])
    maxnodeid = struct.pack("i",h["maxnid"])
    a.write(h["magic"]+version+ts+maxnodeid)

def readhead1(a):        
    """read the main file header"""
    magic = a.read(HEADER_MAGIC_SIZE)
    version = struct.unpack("bbhi",a.read(2+2+4))
    ts = struct.unpack("q",a.read(8))[0]
    maxnodeid = struct.unpack("i",a.read(4))[0]
    if magic != RHMAGIC:
            print "bad magic",magic
            return False
    else:
            #print magic,version,"maxnodeid",maxnodeid,ts
            return dict(version=version,maxnid=maxnodeid,ts=ts,magic=magic)


def writeend(a):
    """writes the end record"""
    w = (MAGIC,0x0B,0,HEADER_SIZE,0)
    h1 = struct.pack("5i",*w)
    h2 = struct.pack("q",0)
    a.write(h1+h2)

def writehead(a,h):
    a.write(struct.pack("5i",MAGIC,h["rt"],h["nid"],h["fs"],h["ps"]) + struct.pack("q",h["h2"]))

def readrechead(a):
    """read record"""
    p = a.tell()
    h1 = a.read(4*5)
    if h1 == "":
            return None
    h2 = a.read(8)
    magic,rt,nid,fs,ps= struct.unpack("5i",h1)
    if magic != MAGIC:
            print "bad magic record",magic
    r = dict(rt=rt,nid=nid,fs=fs,ps=ps,poffset=a.tell(),hoffset=p,nextheader=p+ps+fs,h2=struct.unpack("q",h2)[0])
    return r
