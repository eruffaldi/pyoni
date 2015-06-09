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
# Version 2015/06/09

import struct#
import onifile as oni
import shutil

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
    parser.add_argument('--mjpeg',action="store_true",help="extract the color stream as motion jpeg")
    parser.add_argument('--dump',action="store_true")
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

    if args.fixcut:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        patchaction = True
        action = "fixcut"

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

    elif action == "stripcolor":
        offdict = dict()
        # scan all and keep pre and last
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                if h["nid"] == 1:                
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
    elif action == "rescale":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    t = oni.parsedata(a,h)["timestamp"]
                    t2 = int(t*args.rescale)
                    print h["nid"],t,t2
                    oni.patchtime(a,h,t2)
                elif h["rt"] == oni.RECORD_NODE_ADDED:
                    hh = oni.parseadded(a,h)
                    hh["maxts"] = int(hh["maxts"]*args.rescale)
                    hh["mints"] = int(hh["mints"]*args.rescale)
                    oni.patchadded(a,h,hh)
                elif h["rt"] == oni.RECORD_SEEK_TABLE:
                    x = oni.parseseek(a,h)
                    n = len(x["data"])
                    print "seektable",h["nid"],"of",n
                    for i in range(0,n):
                        x["data"][i]["timestamp"] = int(x["data"][i]["timestamp"]*args.rescale)
                    oni.writeseek(a,h) 
                    
                # next record
                a.seek(h["nextheader"]) #h["fs"]-HEADER_SIZE+h["ps"]+pt,0)        
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

