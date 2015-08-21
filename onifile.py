import struct,sys
from collections import defaultdict
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

def parseindexentry(a):
    """decodes the DataIndexEntry made of a timestamp, config and offset as dictionary"""
    ts = parseint64(a)
    cid = parseint(a)
    pos = parseint64(a)
    return dict(timestamp=ts,config=cid,offset=pos)

def makeindexentry(a):
    """encodes the DataIndexEntry made of a timestamp, config and offset"""
    if type(a) == tuple:
        return struct.pack("=qiq",a[0],a[1],a[2])
    else:
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

#struct RecordHeaderData
#{
#    XnUInt32 magic;
#    XnUInt32 recordType;
#    XnUInt32 nodeId;
#    XnUInt32 fieldsSize;
#    XnUInt32 payloadSize;
#    XnUInt64 undoRecordPos;
#};


def parseint(a):
    return struct.unpack("i",a.read(4))[0]

def parseint64(a):
    return struct.unpack("q",a.read(8))[0]

def makeint64(a):
    return struct.pack("q",a)

def parsedatahead(a,h):
    """Parsed the header of the data block containing timestamp and seek table position
    https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniDataRecords.cpp"""
    a.seek(h["poffset"],0)
    ts =    parseint64(a)
    frameid  = parseint(a)
    return dict(timestamp=ts,frameid=frameid)

def writedatahead(a,h):
    a.seek(h["poffset"],0)
    a.write(struct.pack("=qi",h["timestamp"],h["frameid"]))

def patchtime(a,h,ot):
    a.seek(h["poffset"],0)
    a.write(makeint64(ot))

def parsestr(a):
    namelen = parseint(a)
    name = a.read(namelen)[0:-1]
    return name

def writeseek(a,h):
    print "writeseek",len(h["data"])
    a.seek(h["poffset"],0)
    for x in h["data"]:
        y = makeindexentry(x)
        a.write(y)

def parseseek(a,h):
    a.seek(h["poffset"],0)
    print "seek",h["fs"]
    r = []
    n = h["ps"]/(8+8+4)
    print "reading seektable",n
    for i in range(0,n):
        t = parseindexentry(a)
        r.append(t)
    h["data"] = r
    return h
def makestr(s):
    return struct.pack("=i",len(s)+1)+ s+"\x00" 

codec2id = dict(raw=XN_CODEC_UNCOMPRESSED,jpeg=XN_CODEC_JPEG)
codec2id["16z"] = XN_CODEC_16Z
codec2id["8z"] = XN_CODEC_8Z
codec2id["16zt"] = XN_CODEC_16Z_EMB_TABLES

def patchadded(a,h,hh):
    a.seek(h["poffset"],0)
    a.write(makestr(hh["name"]))
    #print "codecback",codec2id.get(hh["codec"],hh["codec"])
    ocodec = codec2id.get(hh["codec"],hh["codec"])
    print h,hh
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

def writeprop(a,h,z):
    a.seek(h["poffset"],0)
    if h["rt"] == RECORD_INT_PROPERTY:      
        c = makestr(z["name"]) + struct.pack("=ii",4+4,z["data"])
        a.write(c)
    else:
        print "prop type unsupported",h,z



def writehead1(a,h):
    """writes a new header"""
    a.seek(0)
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
    a.write(struct.pack("5i",*w)+struct.pack("q",0))

def copyblock(a,h,b,frame=None,timestamp=None):
    a.seek(h["poffset"],0)
    hout = dict(rt=h["rt"],nid=h["nid"],fs=h["fs"],ps=h["ps"],undopos=h["undopos"],poffset=0,hoffset=b.tell(),nextheader=0)
    writehead(b,hout)
    if h["fs"] > 5*4+8:
        if h["rt"] == RECORD_NEW_DATA and frame is not None:
            # skip real time 
            oldts =    parseint64(a)
            oldframeid  = parseint(a)
            # field or payload?
            b.write(struct.pack("=qi",timestamp,frame))
        else:
            print "extra",h
            b.write(a.read(h["fs"]-(5*4+8)))

    n = 0
    while n < h["ps"]:
        no = h["ps"]-n
        if no > 64*1024:
            no = 64*1024
        d = a.read(no)
        b.write(d)
        n += no
    hout["poffset"] = b.tell()
    hout["nextheader"] = hout["hoffset"] + hout["fs"] + hout["ps"]
    return hout

def writehead(a,h):
    a.write(struct.pack("5i",MAGIC,h["rt"],h["nid"],h["fs"],h["ps"]) + struct.pack("q",h["undopos"]))

def readrechead(a):
    """read record: the resulting dictionary contains:
    - rt  = recordType
    - nid = identifier/stream
    - fs  = field size
    - ps  = payload size
    - poffset = offset to the content
    - hoffset = offset to the header
    - nextheader = next header
    - h2 = undo record pos (one uint64)

    The header stored is:
    - magic (32bit) 0x0052494E
    - rt
    - nid
    - fs = sizeof(*m_header)
    - ps 
    - undorecord
    """
    p = a.tell()
    h1 = a.read(4*5+8)
    if h1 == "":
            return None
    magic,rt,nid,fs,ps,undopos= struct.unpack("=5iq",h1)
    if magic != MAGIC:
            print "bad magic record",magic
    r = dict(rt=rt,nid=nid,fs=fs,ps=ps,poffset=a.tell(),hoffset=p,nextheader=p+ps+fs,undopos=undopos)
    return r


class StreamInfo:
    """Class for transcoding"""
    def __init__(self):
        self.oldtimestamp = 0 # last old times
        self.oldframes = 0 # original frame
        self.oldbasetime = None # of old

        self.newtimestamp = 0 # last new times
        self.newframes = 0 # current writing frame
        self.maxts = None # of new frame
        self.mints = None # of new frame
        self.configid = 0

        self.headerblock = None # ??
        self.headerdata = None # ?? 
        self.framesoffset = [] # stored seek table (timestamp,offset)
    def assignheader(self,h,hh):
        self.headerblock = h
        self.headerdata = hh
    def addframe(self,h,hh,file):
        off = file.tell()
        t = hh["timestamp"]
        self.newtime(t)
        self.framesoffset.append((t,self.configid,off))
        self.newframes += 1
    def newtime(self,t):
        if self.maxts is None:
            self.maxts = t
            self.mints = t
        else:
            if t > self.maxts:
                self.maxts = t
            if t < self.mints:
                self.mints = t
        self.newtimestamp = t
    def writeseek(self,a):
        a.write
        for t in self.framesoffset:
            a.write(makeindexentry(t))
    def patchframeheader(self,a):
        q = self        
        q.headerdata["maxts"] = q.maxts is not None and  q.maxts or 0
        q.headerdata["mints"] = q.mints is not None and  q.mints or 0 
        q.headerdata["frames"] = q.newframes
        patchadded(a,q.headerblock,q.headerdata) 

class Reader:
    def __init__(self,file,h0=None):
        self.file = file
        self.lasth = None
        self.nodeinfo = dict()
        self.nodetype2nid = dict()
        if h0 is None:
            h0 = readhead1(self.file)
        self.h0 = h0
        self.pseektable = None
        self.pend = None
    @property
    def streams(self):
        return self.nodeinfo

    def next(self):
        if self.lasth:
            self.file.seek(self.lasth["nextheader"])
        h = readrechead(self.file)
        self.lasth = h
        if h is None:
            return None
        if h["rt"] == RECORD_NEW_DATA:
            pass
        elif h["rt"] == RECORD_NODE_ADDED:
            hh = parseadded(self.file,h)
            self.nodeinfo[h["nid"]] = hh
            self.nodetype2nid[hh["nodetype"]] = h["nid"]
        elif h["rt"] == RECORD_GENERAL_PROPERTY:
            pp = parseprop(self.file,h)
            if pp["name"] == "xnMapOutputMode":
                (xres,yres) = struct.unpack("ii",pp["data"])
                hhnode = self.nodeinfo[h["nid"]]
                hhnode["size"] = (xres,yres)
        elif h["rt"] == RECORD_NEW_DATA:
            hh = parsedatahead(self.file,h)
            q = self.nodeinfo[hh["nid"]]
            q["maxts"] = hh["timestamp"]
        elif h["rt"] == RECORD_SEEK_TABLE:
            self.pseektable = h
        elif h["rt"] == RECORD_END:
            self.pend = h
        return h

# inplace
class Patcher(Reader):
    def __init__(self,file,h0):
        Reader.__init__(file,h0)
        self.stats = defaultdict(StreamInfo) # for file stats and seek table into b
    def finalize(self):
        for q in self.stats.values():
            print "writing",q
            q.patchframeheader(b)
            q.writeseek(b)
        self.h0["ts"] = max([q.maxts for q in self.stats.values()])
        writehead1(self.file,self.h0)                           
        writeend(self.file)                    

class Writer:
    def __init__(self,file,h0):
        self.file = file
        self.h0 = h0
        self.stats = defaultdict(StreamInfo) # for file stats and seek table into b

    def addproperty(self,header,content):
        writehead(self.file,header) 
        header["poffset"] = self.file.tell()       
        writeprop(self.file,header,content)
    def copyblock(self,header,file):
        writehead(self.file,header)
        file.seek(header["poffset"])
        d = file.read(header["ps"]+header["fs"]-HEADER_SIZE)
        self.file.write(d)

    def addframe(self,nid,h,timestamp,content):
        writehead(self.file,h) 
        header["poffset"] = self.file.tell()       
        writedatahead(self.file,nid=nid,timestamp=timestamp)
        q = stats[h["nid"]]
        q.addframe(h,hh,self.file)
        copyblock(a,h,self.file,frame=q.newframe-1,timestamp=q.timestamp)

        # and then the 
    def finalize(self):
        for q in self.stats.values():
            print "writing",q
            q.patchframeheader(b)
            q.writeseek(b)
        writeend(self.file)                    
        self.h0["ts"] = max([q.maxts for q in self.stats.values()])
        writehead1(self.file,self.h0)       

#                    writehead(b,hc)
#                    b.write(colordata)


#                nidc = r.nodetype2nid[NODE_TYPE_IMAGE]
#               nidd = r.nodetype2nid[NODE_TYPE_DEPTH]
#                q = stats[nidc]
#                q.addframe(h,hh,b)              
#                q = stats[nidd]
#                q.addframe(h,hh,b)
