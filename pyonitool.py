#!/usr/bin/python
# OpenNI ONI tool
# by Emanuele Ruffaldi PERCRO-SSSA 2013-2015
#
# Implemented Operations:
# - time rescale
# - print times
# - fix truncated file
# - extract motion jpeg of color
# - remove color component
#
# Possible future:
# - extract single image/depth
# - split/cut
# - dump stats
#
# TODO: XN_STREAM_PROPERTY_S2D_TABLE
#
# Version 2015/06/09

import struct#
import onifile as oni
import shutil
from collections import defaultdict

class StreamInfo:
    def __init__(self):
        self.frame = 0
        self.newframe = 0
        self.maxts = None
        self.mints = None
        self.basetime = None
        self.headerblock = None
        self.headerdata = None
        self.framesoffset = []
    def newtime(self,t):
        if self.maxts is None:
            self.maxts = t
            self.mints = t
        else:
            if t > self.maxts:
                self.maxts = t
            if t < self.mints:
                self.mints = t

def interval(s,t,tt):
    try:
        x, y = map(tt, s.split(','))
        return x, y
    except:
        raise argparse.ArgumentTypeError("%s must be x,y" % t)


if __name__ == "__main__":
    import sys,os,argparse

    parser = argparse.ArgumentParser(description='Scan OpenNI ONI files')
    parser.add_argument('file',help='ONI filename')
    parser.add_argument('--info',action="store_true")
    parser.add_argument('--times',action="store_true",help="print times of each frame")
    parser.add_argument('--rescale',type=float,default=0.0,help="rescale timings")
    parser.add_argument('--fixcut',action="store_true",help="fixes cut file")
    parser.add_argument('--checkcut',action="store_true",help="checks if file was cut")
    parser.add_argument('--stripcolor',action="store_true")
    parser.add_argument('--stripir',action="store_true",help="removes IR")
    parser.add_argument('--mjpeg',action="store_true",help="extract the color stream as motion jpeg")
    parser.add_argument('--dump',action="store_true")
    parser.add_argument('--dupframes',action="store_true")
    #parser.add_argument('--cutbytime',help="cut by specifing time in seconds: startseconds,endseconds",type=lambda x:interval(x,"time",float))
    #parser.add_argument('--cutbyframe',help="cut by specifing time in frames: startframe,endframe",type=lambda x:interval(x,"time",int))
    parser.add_argument('--output')

    args = parser.parse_args()

    if args.file is None:
        print "Required: ONI filename"
        sys.exit(-1)

    action = ""
    patchaction = False

    if args.rescale != 0:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        patchaction = True
        action = "rescale"

    if args.stripcolor:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "stripcolor"

    if args.stripir:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "stripir"

    if args.fixcut :
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        patchaction = True
        action = "fixcut"

    if args.cutbyframe is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        target = ("frame",args.cutbyframe)
        action = "cutbyframe"

    if args.cutbytime is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        target = ("timeus",[int(x*1E6) for x in args.cutbyframe])
        action = "cutbytime"

    if args.checkcut:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "checkcut"
        args.output = None

    if args.mjpeg:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "mjpeg"

    if args.dump:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "dump"

    if args.info:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "info"

    if args.dupframes:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        patchaction = True
        action = "dupframes"

    filesize = os.stat(args.file).st_size
    if patchaction:
        shutil.copyfile(args.file,args.output)
        args.file = args.output

        print args.file
        a = open(args.file,"r+b")
    else:
        a = open(args.file,"rb")
        if action != "" and args.output is not None:
            b = open(args.output,"wb")

    h0 = oni.readhead1(a)

    mid = 0 # maximum identifier
    prelast = None 
    last = None

    if action == "mjpeg":
        mid = 0 # maximum identifier
        prelast = None 
        last = None
        st = None

        offdict = dict()
        count = 0
        # scan all and keep pre and last
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                if h["nid"] == 2:
                    if h["rt"] == oni.RECORD_NEW_DATA:
                        pd = oni.parsedata(a,h)
                        print pd["dataoffset"],h["ps"],h["fs"]
                        z = a.read(h["ps"])
                        count += 1
                        if count == 50:
                            o = open("x.jpg","wb")
                            o.write(z)
                            o.close()
                            first = False
                        b.write(z)         
                if h["rt"] == oni.RECORD_END:
                    continue
                a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)
        a.close()
        b.close()

    elif action == "stripcolor" or action == "stripir":
        offdict = dict()
        # scan all and keep pre and last
        if action == "stripcolor":
            id = 1
        else:
            id = 2
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                if h["nid"] == id:                
                    if h["rt"] == oni.RECORD_SEEK_TABLE: # skip
                        #st = loadseek(a,h)
                        print "seek loaded and skipped, needs update"
                        a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)
                        continue
                    oni.writehead(b,h)
                    d = a.read(h["ps"]+h["fs"]-oni.HEADER_SIZE)
                    b.write(d)
                    # TODO recompute seek table
                    if h["rt"] == oni.RECORD_NEW_DATA:
                        pd = oni.parsedata(a,h)
                        print pd["dataoffset"],h["ps"]
                if h["rt"] == oni.RECORD_END:
                    oni.writeend(b)
                    continue
                a.seek(h["nextheader"],0)
        a.close()
        b.close()
    elif action == "cutbyframe" or action == "cutbytime":

        stats = defaultdict(StreamInfo)
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    t = oni.parsedata(a,h)["timestamp"]
                    q = stats[h["nid"]]
                    good = False
                    if target[0] == "frame":
                        good = q.frame >= target[1][0] and frame <= target[1][1]
                    else:
                        good = t >= target[1][0] and t <= target[1][1]
                    if good:
                        # retime
                        if q.newframe == 0:
                            q.basetime = t
                        t2 = t-q.basetime
                        q.newtime(t2)
                        # store for seek table
                        self.framesoffset.append((b.tell(),q.newframe))
                        # append block

                        # then next
                        q.newframe += 1
                    q.frame += 1
                elif h["rt"] == oni.RECORD_NODE_ADDED:
                    hh = oni.parseadded(a,h)
                    q = stats[h["nid"]]
                    self.headerblock = h
                    self.headerdata = hh
                    # append block
                elif h["rt"] == oni.RECORD_SEEK_TABLE:
                    # append new seektable
                    pass
                else:
                    # append block
                    pass

                # next record
                a.seek(h["nextheader"]) #h["fs"]-HEADER_SIZE+h["ps"]+pt,0)      

        # patch the stream blocks with maxts/mints and frames
        for nid,q in stats.iteritems():
            q.headerdata["maxts"] = q.maxts
            q.headerdata["mints"] = q.mints
            q.headerdata["frames"] = q.newframe
            if q.mints is None:
                continue
            oni.patchadded(b,q.headerblock,q.headerdata)    
        # patch header 0
        h0["ts"] = max([q.maxts for x in stats.values()])
        oni.writehead1(b,h0)                           
    elif action == "rescale":
        stats = dict()
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    t = oni.parsedata(a,h)["timestamp"]
                    t2 = int(t*args.rescale)
                    #print h["nid"],t,t2
                    q = stats.get(h["nid"],None)
                    if q is None:
                        print "new for",h["nid"],"in new data"
                        q = [t2,t2,None,None]
                        stats[h["nid"]] = q
                    else:
                        if q[0] is None:
                            q[0] = t2
                            q[1] = t2
                        else:
                            if q[0] < t2:
                                q[0] = t2;
                            if q[1] > t2:
                                q[1] = t2
                    oni.patchtime(a,h,t2)
                elif h["rt"] == oni.RECORD_INT_PROPERTY:
                    z = oni.parseprop(a,h)
                    if z["name"] == "IsFrameBased":
                        z["data"] = 0
                        oni.writeprop(a,h,z)
                elif h["rt"] == oni.RECORD_NODE_ADDED:
                    hh = oni.parseadded(a,h)
                    q = stats.get(h["nid"],None)
                    if q is None:
                        print "new for",h["nid"],"in added"
                        q = [None,None,h,hh]
                        stats[h["nid"]] = q
                    else:
                        q[2] = h
                        q[3] = hh
                elif h["rt"] == oni.RECORD_SEEK_TABLE:
                    x = oni.parseseek(a,h)
                    n = len(x["data"])
                    print "seektable",h["nid"],"of",n
                    for i in range(0,n):
                        x["data"][i]["timestamp"] = int(x["data"][i]["timestamp"]*args.rescale)
                    oni.writeseek(a,h) 
                    
                # next record
                a.seek(h["nextheader"]) #h["fs"]-HEADER_SIZE+h["ps"]+pt,0)      
        for k,v in stats.iteritems():
            print "v is",v
            hh = v[3]
            h = v[2]
            hh["maxts"] = v[0]
            hh["mints"] = v[1]
            if v[0] is None:
                continue
            print "patching",a,h["nid"],hh    
            oni.patchadded(a,h,hh)    
        h0["ts"] = max([x[3]["maxts"] for x in stats.values()])
        oni.writehead1(a,h0)                     
    elif action == "dupframes":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                elif h["rt"] == oni.RECORD_SEEK_TABLE:
                    x = oni.parseseek(a,h)
                    y = []
                    # duplicate here....                    
                    h["data"] = x
                    oni.writeseek(a,h) 
                    break
                # next record
                a.seek(h["nextheader"]) #h["fs"]-HEADER_SIZE+h["ps"]+pt,0)                
        # now fix the maxts 
        oni.writeend(a)
    elif action == "fixcut" or action == "checkcut":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                # next record
                a.seek(h["nextheader"]) #h["fs"]-HEADER_SIZE+h["ps"]+pt,0)                
        if True:
            print "prelast",prelast
            print "last",last
            print "maxnodeid",mid

        if not last["nextheader"] <= filesize:
            print "last ends at",last["nextheader"],"with file size",filesize,"delta:",last["nextheader"]-filesize," we need truncate at pre last",prelast["afteroffset"]
            if action == "fixcut":
                a.truncate(prelast["nextheader"])
            last = prelast

        if last["rt"] != oni.RECORD_END:
            print "missing RECORD_END. Last Record is:",last["rt"],"appending"
            if action == "fixcut":
                a.seek(0,2)
                oni.writeend(a)

        if h0["maxnid"] != mid:
            print "bad maxnid",h0["maxnid"],"vs",mid,"fixing"
            h0["maxnid"] = mid
            if action == "fixcut":
                a.seek(0,0)
                oni.writehead1(a,h0)
        else:
            print "header ok, no changes"

    elif args.times:
        while True:
                h = oni.readrechead(a)
                pt = a.tell()
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    print h["nid"],oni.parsedata(a,h)["timestamp"]

                # next record
                a.seek(h["nextheader"],0)
    elif action == "info":
        # for each stream: number of frames, max ts, resolution
        streams ={}
        nodetypes = {}
        nodetypes[2] = "depth"
        nodetypes[3] = "color"
        print "fileheader",h0
        while True:
            h = oni.readrechead(a)
            pt = a.tell()
            if h is None:
                    break
            q = streams.get(h["nid"])
            if q is None:
                q = dict(frames=0)
                streams[h["nid"]] = q
            if h["rt"] == oni.RECORD_NEW_DATA:
                z = oni.parsedata(a,h)
                q["maxts"] = z["timestamp"]
            #elif h["rt"] == oni.RECORD_INT_PROPERTY:
            #    z = oni.parseprop(a,h)
            #    print "intprop",h["nid"],z
            elif h["rt"] == oni.RECORD_NODE_ADDED:
                hh = oni.parseadded(a,h)
                q.update(hh)
                #q["type"] = nodetypes.get(hh["nodetype"],str(hh["nodetype"]))
            elif h["rt"] == oni.RECORD_NODE_DATA_BEGIN:
                break
            elif h["rt"] == oni.RECORD_GENERAL_PROPERTY:
                pp = oni.parseprop(a,h)
                if pp["name"] == "xnMapOutputMode":
                    (xres,yres) = struct.unpack("ii",pp["data"])
                    q["width"] = xres
                    q["height"] = yres
            # next record
            a.seek(h["nextheader"],0)
        for k,v in streams.iteritems():
            print k,v

    elif action == "dump" or action == "":
        # scan all and keep pre and last
        while True:
                h = oni.readrechead(a)
                pt = a.tell()
                if h is None:
                        break
                prelast = last
                last = h0
                if h["nid"] > mid:
                        mid = h["nid"]

                if h["rt"] == oni.RECORD_NEW_DATA:
                    print "newdata",h["nid"],oni.parsedata(a,h),h["ps"]
                elif h["rt"] == oni.RECORD_NODE_DATA_BEGIN:
                    print "nodebegin",h["nid"]
                elif h["rt"] == oni.RECORD_NODE_ADDED:
                    print "nodeadded",h["nid"],oni.parseadded(a,h)
                elif h["rt"] == oni.RECORD_INT_PROPERTY:
                    print "intprop",h["nid"],oni.parseprop(a,h)
                elif h["rt"] == oni.RECORD_GENERAL_PROPERTY:
                    pp = oni.parseprop(a,h)
                    print "genprop",h["nid"],pp
                    if pp["name"] == "xnMapOutputMode":
                        (xres,yres) = struct.unpack("ii",pp["data"])
                        data = dict(xres=xres,yres=yres)
                        print "\t",data
                elif h["rt"] == oni.RECORD_NODE_STATE_READY:
                    print "ready",h["nid"]
                elif h["rt"] == oni.RECORD_NODE_REMOVED:
                    print "removed",h["nid"]
                elif h["rt"] == oni.RECORD_SEEK_TABLE:
                    print "seektable",h["nid"]
                elif h["rt"] == oni.RECORD_END:
                    print "end"
                else:
                    print h["rt"]

                # next record
                a.seek(h["nextheader"],0)

        if True:
            print "prelast",prelast
            print "last",last
            print "maxnodeid",mid
    else:
        print "unknown action",action
    a.close()

