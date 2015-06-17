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
try:
    import xndec
except:
    xndec =None
try:
    import png
except:
    png =None

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
    parser.add_argument('--extractcolor',help="extract the color stream single jpeg or png images. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--extractdepth',help="extract the depth stream single png images. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--extractir',help="extract the depth stream single png images. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--fseek',type=int,default=0,help="seek frame for extract")
    parser.add_argument('--fduration',type=int,default=-1,help="duration of extraction in frames")
    parser.add_argument('--skipframes',type=int,default=None,help="skip n frames")
    parser.add_argument('--dupframes',type=int,default=None,help="duplicate frames")
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

    if False:
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

    subaction = ""
    extractpath = ""
    varia = ['extractcolor','extractdepth','extractir']
    for x in varia:
        if getattr(args,x):
            if action != "":
                print "Already specified action",action
                sys.exit(-1)
            subaction = x
            action = "extract"
            extractpath = getattr(args,x)
            print "extract action",extractpath

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

    if args.dupframes is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "dupframes"

    if args.skipframes is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "skipframes"

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
    stats = defaultdict(oni.StreamInfo)
    needclose = False
    seektableheader = None

    if action == "extract":
        seekframe = args.fseek
        codec = None
        endframe = args.fduration < 0 and -1 or seekframe+args.fduration
        targetnid = -1
        foundhh = None
        ob = None
        extracttype = dict(extractcolor=oni.NODE_TYPE_IMAGE,extractdepth=oni.NODE_TYPE_DEPTH,extractir=oni.NODE_TYPE_IR)[subaction]
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["rt"] == oni.RECORD_NODE_ADDED:
                    hh = oni.parseadded(a,h)
                    print "nidadded",h,hh
                    if hh["nodetype"] == extracttype:
                        print "!!found matching"
                        targetnid = h["nid"]
                        codec = hh["codec"]
                        foundhh = hh
                        if codec == "16zt":
                            if xndec is None or xndec.doXnStreamUncompressDepth16ZWithEmbTable is None:
                                print "xndec is missing cannot decode to png"
                                sys.exit(-1)
                            if png is None:
                                print "pypng is missing"
                                sys.exit(-1)
                elif h["rt"] == oni.RECORD_GENERAL_PROPERTY:
                    pp = oni.parseprop(a,h)
                    if pp["name"] == "xnMapOutputMode" and targetnid == h["nid"]:
                        (xres,yres) = struct.unpack("ii",pp["data"])
                        print "found size",xres,yres,"for",h["nid"]
                        if codec == "16zt":
                            ob = xndec.allocoutput16(xres*yres)
                elif h["nid"] == targetnid:
                    if h["rt"] == oni.RECORD_NEW_DATA:
                        pd = oni.parsedatahead(a,h)
                        if pd["frameid"] >= seekframe and (endframe == -1 or pd["frameid"] < endframe):
                            print pd["frameid"],h["ps"],h["fs"]
                            if codec == "jpeg":
                                ext = "jpeg"
                            elif codec == "16zt":
                                ext = "png"
                            else:
                                ext = "bin"
                            of = open("%s%d.%s" % (extractpath,pd["frameid"],ext),"wb")
                            if codec == "jpeg":
                                of.write(a.read(h["ps"]))
                            elif codec == "16zt":
                                code,size = xndec.doXnStreamUncompressDepth16ZWithEmbTable(a.read(h["ps"]),ob)
                                # save content of ob to PNG 16bit with size xres,yres
                                w = png.Writer(width=xres,height=yres,greyscale=True,bitdepth=16)
                                import array
                                aa = array.array("H")
                                aa.fromstring(ob)
                                w.write(of,[aa[i*xres:(i+1)*xres] for i in range(0,yres)])
                            else:
                                print "unsupported codec",foundhh
                                sys.exit(0)
                            of.close()
                        elif endframe != -1 and pd["frameid"] >= endframe:
                            break
                if h["rt"] == oni.RECORD_END:
                    continue
                a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)        
    elif action == "mjpeg":
        prelast = None 
        last = None
        st = None

        offdict = dict()
        count = 0
        targetnid = None
        # scan all and keep pre and last
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["rt"] == oni.RECORD_NODE_ADDED:
                    hh = oni.parseadded(a,h)
                    if hh["nodetype"] == oni.NODE_TYPE_IMAGE:
                        targetnid = h["nid"]
                elif h["nid"] == targetnid:
                    if h["rt"] == oni.RECORD_NEW_DATA:
                        pd = oni.parsedatahead(a,h)
                        if pd["frameid"] >= seekframe and (endframe == -1 or pd["frameid"] < endframe):
                            print pd["frameid"],h["ps"],h["fs"]
                            b.write(a.read(h["ps"]))         
                        elif endframe != -1 and pd["frameid"] >= endframe:
                            break
                if h["rt"] == oni.RECORD_END:
                    continue
                a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)
    elif action == "stripcolor" or action == "stripir":
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
                        break
                        #st = loadseek(a,h)
                        print "seek loaded and skipped, needs update"
                        a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)
                        continue
                    oni.writehead(b,h)
                    d = a.read(h["ps"]+h["fs"]-oni.HEADER_SIZE)
                    b.write(d)
                    # TODO recompute seek table
                    if h["rt"] == oni.RECORD_NEW_DATA:
                        pd = oni.parsedatahead(a,h)
                        print pd["frameid"],h["ps"]
                if h["rt"] == oni.RECORD_END:
                    oni.writeend(b)
                    continue
                a.seek(h["nextheader"],0)
        needclose = True
    elif action == "cutbyframe" or action == "cutbytime":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    t = oni.parsedatahead(a,h)["timestamp"]
                    q = stats[h["nid"]]
                    good = False
                    if target[0] == "frame":
                        good = q.oldframes >= target[1][0] and q.oldframes <= target[1][1]
                    else:
                        good = t >= target[1][0] and t <= target[1][1]
                    if good:
                        # retime
                        if q.newframes == 0:
                            q.oldbasetime = t
                        t2 = t-q.oldbasetime

                        #q.newtime(t2)
                        #q.addframe() 
                        #q.copyblock()
                        #self.framesoffset.append((b.tell(),q.newframe))

                    q.oldframes += 1
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
        needclose = True
    elif action == "rescale":
        # TODO update with StreamInfo
        stats = dict()
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    t = oni.parsedatahead(a,h)["timestamp"]
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
        needclose = True
    elif action == "dupframes":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                if h["rt"] == oni.RECORD_SEEK_TABLE:
                    # TODO gen seek
                    pass
                elif h["rt"] == oni.RECORD_NEW_DATA:
                    hh = oni.parsedatahead(a,h)
                    q = stats[h["nid"]]
                    for i in range(0,args.dupframes):
                        q.addframe(h,hh,b)
                        oni.copyblock(a,h,b,frame=q.newframe-1,timestamp=q.timestamp)
                a.seek(h["nextheader"])
        needclose = True
    elif action == "skipframes":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                if h["rt"] == oni.RECORD_SEEK_TABLE:
                    # TODO gen seek
                    pass
                elif h["rt"] == oni.RECORD_NODE_ADDED:
                    hh = oni.parseadded(a,h)
                    stats[h["nid"]].assignheader(h,hh) 
                elif h["rt"] == oni.RECORD_NEW_DATA:
                    hh = oni.parsedatahead(a,h)
                    q = stats[h["nid"]]
                    if (q.oldframes % args.skipframes) == 0:
                        q.addframe(h,hh,b)
                        oni.copyblock(a,h,b,frame=q.newframes-1,timestamp=q.newtimestamp)
                    q.oldframes += 1
                a.seek(h["nextheader"])
        needclose = True
    elif action == "fixcut" or action == "checkcut":
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                elif h["rt"] == oni.RECORD_NEW_DATA:
                    hh = oni.parsedatahead(a,h)
                    q = stats[h["nid"]]
                    q.addframe(h,hh)
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
            needclose = True

        if last["rt"] != oni.RECORD_END:
            print "missing RECORD_END. Last Record is:",last["rt"],"appending"
            if action == "fixcut":
                a.seek(0,2)
                oni.writeend(a)
                needclose = True

        if h0["maxnid"] != mid:
            print "bad maxnid",h0["maxnid"],"vs",mid,"fixing"
            h0["maxnid"] = mid
            if action == "fixcut":
                a.seek(0,0)
                oni.writehead1(a,h0)
                needclose = True
        else:
            print "header ok, no changes"

    elif args.times:
        while True:
                h = oni.readrechead(a)
                pt = a.tell()
                if h is None:
                        break
                if h["rt"] == oni.RECORD_NEW_DATA:
                    print h["nid"],oni.parsedatahead(a,h)["timestamp"]

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
                z = oni.parsedatahead(a,h)
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
                    print "newdata",h["nid"],oni.parsedatahead(a,h),h["ps"]
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

    if needclose:
        # if need to close first PATCH the NODE ADDED
        # then patch the writeseek        
        for q in stats.values():
            print "writing",q
            q.patchframeheader(b)
            q.writeseek(b)
        h0["ts"] = max([q.maxts for q in stats.values()])
        oni.writehead1(b,h0)                           
    a.close()

