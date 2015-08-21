import onifile as oni
import struct
from collections import defaultdict

def copy(args,a,b):
    r = oni.Reader(a)
    print "firstheader",r.h0
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
            w.addframe(h["nid"],hh["frameid"],hh["timestamp"],a.read(h["ps"]))
        else:
        	w.copyblock(h,a)

    w.finalize()

def strip(args,action,a,b):
    # scan all and keep pre and last
    r = oni.Reader(a)
    w = oni.Writer(b)

    ignoredtype = dict(stripcolor=oni.NODE_TYPE_IMAGE,stripdepth=oni.NODE_TYPE_DEPTH,stripir=oni.NODE_TYPE_IR)[action]
    ignoredid = -1
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_NODE_ADDED:
            hh = oni.parseadded(a,h)
            if hh["nodetype"] == ignoredtype:
            	ignoredid = h["nid"]
            else:
	        	w.copyblock(h,a)
        elif h["nid"] == ignoredid:
        	continue
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
        	w.emitseek(h["nid"])
        elif h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)            
            print dict(nid=h["nid"],ps=h["ps"],fs=h["fs"],frameid=hh["frameid"],timestamp=hh["timestamp"])
            w.addframe(h["nid"],hh["frameid"],hh["timestamp"],a.read(h["ps"]))
        else:
        	w.copyblock(h,a)
    w.finalize()
"""
def cut(args,action,a,b):
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
"""

def skip(args,a,b):
    r = oni.Reader(a)
    w = oni.Writer(b)
    qf = defaultdict(lambda: 0)
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
        	w.emitseek(h["nid"])
        elif h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)
            oldframe = qf[h["nid"]]
            if (oldframe % args.skipframes) == 0:
	            w.addframe(h["nid"],hh["frameid"],hh["timestamp"],a.read(h["ps"]))
            qf[h["nid"]] += 1
        else:
        	w.copyblock(h,a)
    w.finalize()

def dupframes(args,a):
    r = oni.Reader(a)
    w = oni.Writer(b)
    dt = 13 #ms
    qf = dict()
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
        	w.emitseek(h["nid"])
        elif h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)
            dd = a.read(h["ps"])
            qff = qf.get(h["nid"])
            if qff is None:
            	qff = [hh["frameid"],hh["timestamp"]]
            	qf[h["nid"]] = qff
            for i in range(0,args.dupframes):
	            w.addframe(h["nid"],qf["frameid"],qf["timestamp"],dd)
	            qf["frameid"] += 1
	            qf["timestamp"] += dt
        else:
        	w.copyblock(h,a)
    w.finalize()

