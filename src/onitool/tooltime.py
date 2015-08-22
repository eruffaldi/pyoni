from . import onifile as oni
import struct
from collections import defaultdict


def rescale(args,factor,a,b):
    r = oni.Reader(a)
    w = oni.Writer(b,r.h0)
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
            w.emitseek(h["nid"])
        elif h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)            
            print dict(nid=h["nid"],ps=h["ps"],fs=h["fs"],frameid=hh["frameid"],timestamp=hh["timestamp"])
            w.addframe(h["nid"],hh["frameid"],factor*hh["timestamp"],a.read(h["ps"]))
        else:
            w.copyblock(h,a)
    w.finalize()

"""
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
"""