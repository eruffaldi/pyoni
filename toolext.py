

def extractmjpeg(args,a):
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
def extract(args,a):
        seekframe = args.fseek
        codec = None
        endframe = args.fduration < 0 and -1 or seekframe+args.fduration
        targetnid = -1
        foundhh = None
        ob = None
        extracttype = dict(extractboth=-1,extractcolor=oni.NODE_TYPE_IMAGE,extractdepth=oni.NODE_TYPE_DEPTH,extractir=oni.NODE_TYPE_IR)[subaction]
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
                elif h["rt"] == oni.RECORD_GENERAL_PROPERTY:
                    pp = oni.parseprop(a,h)
                    if pp["name"] == "xnMapOutputMode" and targetnid == h["nid"]:
                        (xres,yres) = struct.unpack("ii",pp["data"])
                        print "found size",xres,yres,"for",h["nid"],codec
                        if codec == "16zt":
                            ob = xndec.allocoutput16(xres*yres)
                elif h["nid"] == targetnid:
                    if h["rt"] == oni.RECORD_NEW_DATA:
                        pd = oni.parsedatahead(a,h)
                        if pd["frameid"] >= seekframe and (endframe == -1 or pd["frameid"] < endframe):
                            print "newdata",pd["frameid"],h["ps"],h["fs"],codec
                            if codec == "jpeg":
                                ext = "jpeg"
                            elif codec == "16zt":
                                ext = "png"
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
                if h["rt"] == oni.RECORD_END:
                    continue
                a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)