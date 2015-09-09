import struct#
from . import onifile as oni
import shutil,io
import array,os
import bisect
from collections import defaultdict
from anyregistration import anyregistration
from PIL import Image
from xndec import xndec as xndec
try:
    import png
except:
    png =None


class AsusModel:
    def __init__(self):
        self.size = (640,480)
        self.Drgb = (0.041623, -0.105707, -0.001538, 0.000755, 0.0)
        self.Ddepth = (0.041623, -0.105707, -0.001538, 0.000755, 0.0)
        self.Krgb = (533.9089, 0.0, 321.09951,    0.0, 534.555793, 237.786129,    0.0, 0.0, 1.0)
        self.Kdepth = (570, 0.0, 320,   0.0, 570, 240,    0.0, 0.0, 1.0)
        self.R = (1,0,0,  0,1,0, 0,0,1)
        self.T = (0.0222252,0,0)

def register(args,action,a,b):

    model = AsusModel()
	# scan first and emit second
    depthseen = False
    colorseen = False
    device = "asusxtion"
    ob = None
    depthdataout = None
    colordataout = None
    maxoutdepth = 5000

    r = oni.Reader(a)
    w = oni.Writer(b,r.h0)

    modifycolor = action == "registercolor" # color from depth or the opposite, means that we can directly store one of the two
    nidd = None
    nidc = None
    # parse all metadata and copy
    ignore = set([oni.RECORD_NEW_DATA,oni.RECORD_END,oni.RECORD_SEEK_TABLE,oni.RECORD_NODE_REMOVED])
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_NEW_DATA:
            continue # otherwise no seek
        elif h["rt"] in ignore:
            print "ignored",h["rt"]
            continue
        #TODO mark registered
        #        elif h["rt"] == oni.RECORD_INT_PROPERTY:
        #            z = oni.parseprop(a,h)
        #            print z["name"]
        #            if z["name"] == "registrationType":
        #                z["data"] = 2
        #            # TODO append block property
        #            #w.addproperty(h,z)        else:
        else:
            w.copyblock(h,a)
    # then start iterating the frames
    idd = r.nodetype2nid[oni.NODE_TYPE_DEPTH]
    idc = r.nodetype2nid[oni.NODE_TYPE_IMAGE]
    td = r.getseektable(idd)
    tc = r.getseektable(idc)
    if tc is None:
        raise "Missing color"
    if td is None:
        raise "Missing depth"        
    tc["nid"] = idc
    td["nid"] = idd
    tc["times"] = [x["timestamp"] for x in tc["data"]]
    td["times"] = [x["timestamp"] for x in td["data"]]

    def findnearest(index,time):
        a = index["times"]
        i = bisect.bisect_left(a,time)
        # time <= a[i]
        if i == 0:
            if len(a) < 2:
                return 0
            else:
                i = 1 # 0 is bad
        if i < 2 or i >= len(a)-1:
            if i >= len(a)-1:
                i = len(a)-1
            return (i,index["data"][i])
        else:
            next = a[i] 
            pre = a[i-1]
            if (next-time) < (time-pre):
                return (i,index["data"][i])
            else:
                return (i-1,index["data"][i-1])


    # given the primary 
    if modifycolor:
        primary = td
        secondary = tc
    else:
        primary = tc
        secondary = td

    # statistics
    if False:
        dtimes = []
        dframes = []
        for x in primary["data"]:
            fi,f = findnearest(secondary,x["timestamp"])
            dtimes.append(f["timestamp"]-x["timestamp"])
            dframes.append(f["frameid"]-x["frameid"])
            print x["frameid"],f["frameid"],x["timestamp"],f["timestamp"],(f["frameid"]-x["frameid"]),(f["timestamp"]-x["timestamp"]),(f["offset"]-x["offset"])
        print "time min",min(dtimes),"max",max(dtimes)
        print "frame min",min(dframes),"max",max(dframes)

    for primaryframe in primary["data"]:
        fi,secondaryframe = findnearest(secondary,primaryframe["timestamp"])

        # TODO: support for by frame matching, simply: f = secondary[x["frameid"]]
        if args.fduration > -1 and primaryframe["frameid"] > args.fduration:
            break

        # skip dummy first
        if primaryframe["frameid"] == 0 or secondaryframe["frameid"] == 0:
            continue

        for i in range(0,2): #maybe just (primaryframe,secondaryframe)
            hh = i == 0 and primaryframe or secondaryframe

            a.seek(hh["offset"]) # to data
            h = oni.readrechead(a)
            hhreal = oni.parsedatahead(a,h)
            print h,hhreal
            nid = h["nid"]

            # TODO support for sizes different among streams
            hhnode = r.streams[nid]
            codec = hhnode["codec"]            
            size = hhnode["size"]
            xres,yres = size

            #TODO allow for other encodings
            if codec == "jpeg":
                rawdata = a.read(h["ps"])             
                # decompress always
                b = io.BytesIO()
                b.write(rawdata)
                b.seek(0)
                inc_i = Image.open(b)

                # AS COLOR
                hc = hh
                if not modifycolor:
                    # preserve color as compressed
                    w.addframe(nid,hh["frameid"],hh["timestamp"],rawdata)
                colordata = inc_i.tostring() #Image.tobytes(inc_i,encoder_name='raw')
            elif codec == "16zt":
                rawdata = a.read(h["ps"])
                if ob is None:
                    ob = xndec.allocoutput16(xres*yres)
                xndec.doXnStreamUncompressDepth16ZWithEmbTable(rawdata,ob)
                aa = array.array("H")
                aa.fromstring(ob)

                # AS DEPTH
                depthdata = aa
                hd = hh
                if modifycolor:
                    # depth is preserved in depthmode
                    w.addframe(nid,hh["frameid"],hh["timestamp"],rawdata)
            else:
                print "unsupported codec",codec


        print "registering ",modifycolor and "newcolor" or "newdepth","depthframe(frame,time)",(hd["frameid"],hd["timestamp"]),"colorframe(frame,time)",(hc["frameid"],hc["timestamp"]),"deltaframe(c-d)(frame,time)",(hc["frameid"]-hd["frameid"],hc["timestamp"]-hd["timestamp"])
        if modifycolor:
            #anyregistration on (colordata,depthdata) -> colordataout
            # autoalloc
            print depthdata.__class__,len(depthdata),colordata.__class__,len(colordata),size
            colordataout = anyregistration.doregister2color(colordataout,depthdata,colordata,size,model.Drgb,model.Krgb,size,model.Ddepth,model.Kdepth,model.R,model.T)
            im = Image.frombytes("RGB", size, colordataout.raw, decoder_name='raw')
            b = io.BytesIO()
            im.save(b, 'JPEG')
            w.addframe(idc,hd["frameid"],args.registersynctime and hd["timestamp"] or hc["timestamp"],b.getvalue()) # keep timestamp, discard frameid
            print "\tcompressed from",xres*yres*3,"to",len(b.getvalue())
            # TODO add option for faking timestamp
        else:
            #anyregistration (colordata,depthdata) -> depthdataout
            depthdataout = anyregistration.doregister2depth(depthdataout,depthdata,colordata,size,model.Drgb,model.Krgb,size,model.Ddepth,model.Kdepth,model.R,model.T)
            print "\tgenerated",depthdataout.__class__,len(depthdataout)
            status,size = xndec.doXnStreamCompressDepth16ZWithEmbTable(depthdataout,ob,maxoutdepth)
            print "\tcompressed from",xres*yres*2,"to",size
            w.addframe(idd,hc["frameid"],args.registersynctime and hc["timestamp"] or hd["timestamp"],ob[0:size]) # keep timestamp, discard frameid
            # TODO add option for faking timestamp

    #TODO
    #end
    #removed DEVICE  --> MISSING
    #removed IMAGE   --> 
    #seektable IMAGE
    #removed DEPTH   --> 
    #seektable DEPTH
    w.finalize()


