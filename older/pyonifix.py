# OpenNI ONI fixer
#
# by Emanuele Ruffaldi PERCRO-SSSA 2013
#
# USE AT YOUR OWN RISK - ALWAYS BACKUP THE FILE
#
# Possible future:
# - split/cut/extract
# - dump stats
#
# References:
#https://github.com/OpenNI/OpenNI2/blob/master/Source/Drivers/OniFile/DataRecords.cpp
#https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniRecorder.cpp
#https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniDataRecords.cpp

import struct

RECORD_END = 0x0B
HEADER_MAGIC_SIZE = 4
MAGIC = 0x0052494E
MAGICS = "NIR\0"
RHMAGIC = "NI10"
HEADER_SIZE = 4*5+8


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
            print magic,version,"maxnodeid",maxnodeid,ts
            return dict(version=version,maxnid=maxnodeid,ts=ts,magic=magic)

def writeend(a):
    """writes the end record"""
    w = (MAGIC,0x0B,0,HEADER_SIZE,0)
    h1 = struct.pack("5i",*w)
    h2 = struct.pack("q",0)
    a.write(h1+h2)

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
    r = dict(rt=rt,nid=nid,fs=fs,ps=ps,poffset=a.tell(),hoffset=p,afteroffset=p+ps+fs-HEADER_SIZE)
    # hoffset is begin of header
    # poffset is begin of payload
    # afteroffset is after the record
    return r

def checkvalid(h,s):
    """check if the packet is inside"""
    return h["afteroffset"] <= s


if __name__ == "__main__":
    import sys,os

    if len(sys.argv) == 0:
        print "Required: ONI filename"
        sys.exit(-1)

    filesize = os.stat(sys.argv[1]).st_size
    a = open(sys.argv[1],"r+b")
    h0 = readhead1(a)



    mid = 0 # maximum identifier
    prelast = None 
    last = None

    # scan all and keep pre and last
    while True:
            h = readrechead(a)
            if h is None:
                    break
            prelast = last
            last = h
            if h["nid"] > mid:
                    mid = h["nid"]
            a.seek(h["fs"]-HEADER_SIZE+h["ps"],1)

    if True:
        print "prelast",prelast
        print "last",last
        print "maxnodeid",mid

    if not checkvalid(last,filesize):
        print "last ends at",last["afteroffset"],"with file size",filesize,"delta:",last["afteroffset"]-filesize," we need truncate at pre last",prelast["afteroffset"]
        a.truncate(prelast["afteroffset"])
        last = prelast

    if last["rt"] != RECORD_END:
        print "missing RECORD_END. Last Record is:",last["rt"],"appending"
        a.seek(0,2)
        writeend(a)

    if h0["maxnid"] != mid:
        print "bad maxnid",h0["maxnid"],"vs",mid,"fixing"
        h0["maxnid"] = mid
        a.seek(0,0)
        writehead1(a,h0)
    else:
        print "header ok, no changes"

    a.close()
