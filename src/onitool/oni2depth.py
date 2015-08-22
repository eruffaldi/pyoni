# Extracts a singla RAW depth file of contiguous data
#
# Requires to build xndec
import struct
from onifile import *
from xndec import *

if __name__ == "__main__":
    import sys,os

    if len(sys.argv) == 0:
        print "Required: ONIfilename"
        sys.exit(-1)

    docolor = len(sys.argv) > 3

    filesize = os.stat(sys.argv[1]).st_size
    a = open(sys.argv[1],"rb")
    h0 = readhead1(a)


    mid = 0 # maximum identifier
    prelast = None 
    last = None
    st = None

    offdict = dict()
    count = 0
    ob = allocoutput16(512*424)
    # scan all and keep pre and last
    while True:
            h = readrechead(a)
            if h is None:
                    break
            prelast = last
            last = h
            if h["nid"] > mid:
                    mid = h["nid"]
            if h["nid"] == 1:
                if h["rt"] == RECORD_NEW_DATA:
                    pd = parsedata(a,h)
                    print pd["dataoffset"],h["ps"],h["fs"]
                    z = a.read(h["ps"])
                    count += 1
                    if count == 50:
                        code,size = doXnStreamUncompressDepth16ZWithEmbTable(z,ob)
                        print "decoded ",code,size,"vs input",len(z),"output",len(ob)

                        o = open("x.depth","wb")
                        o.write(ob)
                        o.close()
                        break
            if h["rt"] == RECORD_END:
                continue
            a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)

    a.close()
