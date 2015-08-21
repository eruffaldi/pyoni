import struct#
import onifile as oni
import shutil
import array,os
from collections import defaultdict
import anyregistration.anyregistration as anyregistration
try:
    import xndec
except:
    xndec =None
try:
    import png
except:
    png =None



def register(args,input,output):
	# scan first and emit second
    depthseen = False
    colorseen = False
    needgen = False
    device = "asusxtion"

    r = oni.Reader(a,h0)
    w = oni.Writer(b,h0)

    modifycolor = True # color from depth or the opposite, means that we can directly store one of the two

    h = r.next()
    while h:
        if h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)
            print "newdata",pd["frameid"],h["ps"],h["fs"],codec 
            hhnode = r.nodeinfo[hh["nid"]]
            codec = r.hhnode["codec"]            
            if codec == "jpeg":
            	#TODO d = a.read(h["ps"]+h["fs"]-oni.HEADER_SIZE)
            	colordata = a.read(h["ps"])            	
            	colorseen = True
            	if not modifycolor:
            		# emit colordata
            		w.addframe(h["nid"],h,colordata)
            		pass
            	if depthseen:
            		needgen = True
            elif codec == "16zt":
            	ob = hhnode["ob"]
            	data = a.read(h["ps"])
            	if modifycolor:
            		# emit as it is
            		w.addframe(h["nid"],h,data)
            		pass
                xndec.doXnStreamUncompressDepth16ZWithEmbTable(data,ob)
                aa = array.array("H")
                aa.fromstring(ob)
                depthdata = ob
                depthseen = True
            	if colorseen:
            		needgen = True
            else:
            	print "unsupported codec",codec
            if needgen:
        		# register and emit both using depthdata and colordata
        		colorseen = False
        		depthseen = False
        		# anyregistration
        		# TODO compress
        		# store NODE_ADDED into b
        		#hc = ...
        		#hd = ...

        		if modifycolor:
		            w.addframe(nidd,hc,colordata)
        			# pass
        		else:
		            w.addframe(nidd,hd,depthdata)
        		pass
            # TODO emit exact same block
        elif h["rt"] == oni.RECORD_NODE_ADDED:
			w.copyblock(h,a)
        elif h["rt"] == oni.RECORD_GENERAL_PROPERTY:
            pp = oni.parseprop(a,h)
            if pp["name"] == "xnMapOutputMode" and targetnid == h["nid"]:
	        	q = r.nodeinfo[h["nid"]]
	        	if q["codec"] == "16zt":
	        		xres,yres = q["size"]
	                q["ob"] = xndec.allocoutput16(xres*yres)
			w.copyblock(h,a)
        elif h["rt"] == oni.RECORD_INT_PROPERTY:
            z = oni.parseprop(a,h)
            print z["name"]
            if z["name"] == "registrationType":
                z["data"] = 2
            # TODO append block property
            #w.addproperty(h,z)
        elif h["rt"] == oni.RECORD_SEEK_TABLE or h["rt"] == oni.RECORD_END:
            pass
        else:
            w.copyblock(h,a)
            print "unhandled",h["rt"]
            # append block as it is
            # TODO copy append
    h = r.next()
    # close b seek table
    # close b file
    w.finalize()
