import onifile as oni
import struct,array
try:
    import xndec
except:
    xndec = None
try:
    import png
except:
    png =None

def extractmjpeg(args,a,b):
    targetnid = None
    seekframe = args.fseek
    endframe = args.fduration < 0 and -1 or seekframe+args.fduration
    # scan all and keep pre and last
    r = oni.Reader(a)
    while True:
        h = r.next()
        if h is None:
            break
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

# TODO extract both
def extract(args,action,extractpath,a):
    codec = None
    foundhh = None
    ob = None
    extracttype = dict(extractboth=-1,extractcolor=oni.NODE_TYPE_IMAGE,extractdepth=oni.NODE_TYPE_DEPTH,extractir=oni.NODE_TYPE_IR)[action]
    targetnid = None

    seekframe = args.fseek
    endframe = args.fduration < 0 and -1 or seekframe+args.fduration
    # scan all and keep pre and last
    r = oni.Reader(a)
    while True:
        h = r.next()
        if h is None:
            break
        if h["rt"] == oni.RECORD_NODE_ADDED:
            hh = oni.parseadded(a,h)
            if hh["nodetype"] == extracttype:
                targetnid = h["nid"]
                codec = hh["codec"]
                foundhh = hh
                print "!!found matching for ",targetnid,codec
                if codec == "16zt":
                    if xndec is None or xndec.doXnStreamUncompressDepth16ZWithEmbTable is None:
                        print "xndec is missing cannot decode to png"
                        sys.exit(-1)
                    if png is None:
                        print "pypng is missing"
                        sys.exit(-1)
        elif h["nid"] == targetnid:
            if h["rt"] == oni.RECORD_NEW_DATA:
                pd = oni.parsedatahead(a,h)
                if pd["frameid"] >= seekframe and (endframe == -1 or pd["frameid"] < endframe):
                    print "newdata",pd["frameid"],h["ps"],h["fs"],codec
                    q = r.streams[h["nid"]]
                    xres,yres = q["size"]
                    if codec == "jpeg":
                        ext = "jpeg"
                    elif codec == "16zt":
                        ext = "png"
                        if ob is None:
                            ob = xndec.allocoutput16(xres*yres)
                    else:
                        ext = "bin"
                    outfile = "%s%d.%s" % (extractpath,pd["frameid"],ext)
                    print outfile,codec
                    of = open(outfile,"wb")
                    if codec == "jpeg":
                        of.write(a.read(h["ps"]))
                    elif codec == "16zt":
                        code,size = xndec.doXnStreamUncompressDepth16ZWithEmbTable(a.read(h["ps"]),ob)
                        aa = array.array("H")
                        aa.fromstring(ob)
                        rows = [aa[i*xres:(i+1)*xres] for i in range(0,yres)]
                        if args.coloreddepth:                                    
                            # save content of ob to PNG 16bit with size xres,yres
                            w = png.Writer(width=xres,height=yres,greyscale=True,bitdepth=8)
                            w.write(of,[[int(x*255.0/8000.0) for x in y] for y in rows])
                        else:
                            # save content of ob to PNG 16bit with size xres,yres
                            w = png.Writer(width=xres,height=yres,greyscale=True,bitdepth=16)
                            w.write(of,rows)
                    else:
                        print "unsupported codec",foundhh
                        sys.exit(0)
                    of.close()
                elif endframe != -1 and pd["frameid"] >= endframe:
                    break