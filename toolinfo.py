import onifile as oni
import struct

def info(args,a):
    r = oni.Reader(a)
    print "fileheader",r.h0
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_NEW_DATA:
            break
    for k,v in r.streams.iteritems():
        print k,v

def times(args,a):
    """prints times"""
    r = oni.Reader(a)
    while True:
        h = r.next()
        if h is None:
            break
        if h["rt"] == oni.RECORD_NEW_DATA:
            print h["nid"],oni.parsedatahead(a,h)["timestamp"]

def dump(args,a):
    r = oni.Reader(a)
    last = None
    # scan all and keep pre and last
    mid = -1
    while True:
        h = r.next()
        pt = a.tell()
        if h is None:
            break
        prelast = last
        last = h
        if mid < h["nid"]:
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
    if True:
        print "prelast",prelast
        print "last",last
        print "maxnodeid",mid   
