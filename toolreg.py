import struct#
import onifile as oni
import shutil,io
import array,os
from collections import defaultdict
import anyregistration.anyregistration as anyregistration
from PIL import Image
try:
    import xndec
except:
    xndec =None
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

def register(args,a,b):

    model = AsusModel()
	# scan first and emit second
    depthseen = False
    colorseen = False
    needgen = False
    device = "asusxtion"
    ob = None
    depthdataout = None
    colordataout = None
    maxoutdepth = 5000

    r = oni.Reader(a)
    w = oni.Writer(b,r.h0)

    modifycolor = not args.registerusedepth # color from depth or the opposite, means that we can directly store one of the two
    nidd = None
    nidc = None
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
            w.emitseek(h["nid"])
        elif h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)    
            if args.fduration > -1 and hh["frameid"] > args.fduration:
                continue        
            print dict(nid=h["nid"],ps=h["ps"],fs=h["fs"],frameid=hh["frameid"],timestamp=hh["timestamp"])

            # TODO support for sizes different among streams
            hhnode = r.streams[h["nid"]]
            codec = hhnode["codec"]            
            size = hhnode["size"]
            xres,yres = size

            if codec == "jpeg":
                colordata = a.read(h["ps"])             
                colorseen = True
                if not modifycolor:
                    w.addframe(h["nid"],hh["frameid"],hh["timestamp"],colordata)
                    pass
                else:
                    b = io.BytesIO()
                    b.write(colordata)
                    b.seek(0)
                    inc_i = Image.open(b)
                    colordata = inc_i.tostring() #Image.tobytes(inc_i,encoder_name='raw')
                    hc = hh
                    nidc = h["nid"]
                if depthseen:
                    needgen = True
            elif codec == "16zt":
                data = a.read(h["ps"])
                if modifycolor:
                    w.addframe(h["nid"],hh["frameid"],hh["timestamp"],data)
                    pass
                else:
                    nidd = h["nid"]
                    hd = hh
                if ob is None:
                    ob = xndec.allocoutput16(xres*yres)
                xndec.doXnStreamUncompressDepth16ZWithEmbTable(data,ob)
                aa = array.array("H")
                aa.fromstring(ob)
                depthdata = aa
                depthseen = True
                if colorseen:
                    needgen = True
            else:
                print "unsupported codec",codec
            if needgen:
                if modifycolor:
                    #anyregistration on (colordata,depthdata) -> colordataout
                    # autoalloc


                    print depthdata.__class__,len(depthdata),colordata.__class__,len(colordata),size
                    colordataout = anyregistration.doregister2color(colordataout,depthdata,colordata,size,model.Drgb,model.Krgb,size,model.Ddepth,model.Kdepth,model.R,model.T)
                    im = Image.frombytes("RGB", size, colordataout.raw, decoder_name='raw')
                    b = io.BytesIO()
                    im.save(b, 'JPEG')
                    w.addframe(nidc,hc["frameid"],hc["timestamp"],b.getvalue())
                    print "compressed from",xres*yres*3,"to",len(b.getvalue())
                else:
                    #anyregistration (colordata,depthdata) -> depthdataout
                    depthdataout = anyregistration.doregister2depth(depthdataout,depthdata,colordata,size,model.Drgb,model.Krgb,size,model.Ddepth,model.Kdepth,model.R,model.T)
                    print "generated",depthdataout.__class__,len(depthdataout)
                    status,size = xndec.doXnStreamCompressDepth16ZWithEmbTable(depthdataout,ob,maxoutdepth)
                    print "compressed from",xres*yres*2,"to",size
                    w.addframe(nidd,hd["frameid"],hd["timestamp"],ob[0:size])
                colorseen = False
                depthseen = False
        else:
            w.copyblock(h,a)

    w.finalize()

#TODO mark registered
#        elif h["rt"] == oni.RECORD_INT_PROPERTY:
#            z = oni.parseprop(a,h)
#            print z["name"]
#            if z["name"] == "registrationType":
#                z["data"] = 2
#            # TODO append block property
#            #w.addproperty(h,z)
#        elif h["rt"] == oni.RECORD_SEEK_TABLE or h["rt"] == oni.RECORD_END:
