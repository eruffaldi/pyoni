from . import onifile as oni
import struct
from collections import defaultdict

def copy(args,a,b):
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
            w.addframe(h["nid"],hh["frameid"],hh["timestamp"],a.read(h["ps"]))
        else:
            w.copyblock(h,a)

    w.finalize()

def cut(args,target,a,b):
    r = oni.Reader(a)
    w = oni.Writer(b,r.h0)
    qf = dict()
    while True:
        h = r.next()
        if h is None:
            break
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
            w.emitseek(h["nid"])
        elif h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)            
            # check timestamp/frame
            if target[0] == "frame":
                good = hh["frameid"] >= target[1][0] and hh["frameid"] <= target[1][1]
            else:
                good = hh["timestamp"] >= target[1][0] and hh["timestamp"] <= target[1][1]
            if good:
                qff = qf.get(h["nid"])
                if qff is None:
                    qff = hh # original
                    qf[h["nid"]] = qff
                print dict(nid=h["nid"],ps=h["ps"],fs=h["fs"],frameid=hh["frameid"],timestamp=hh["timestamp"])
                w.addframe(h["nid"],hh["frameid"]-qff["frameid"]+1,hh["timestamp"]-qff["timestamp"],a.read(h["ps"]))
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

def dupframes(args,a,b):
    r = oni.Reader(a)
    w = oni.Writer(b)
    dt = 33333 #ms virtual
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
                qff = dict(frameid=hh["frameid"],timestamp=hh["timestamp"])
                qf[h["nid"]] = qff
            for i in range(0,args.dupframes):
                w.addframe(h["nid"],qff["frameid"],qff["timestamp"],dd)
                qff["frameid"] += 1
                qff["timestamp"] += dt
        else:
            w.copyblock(h,a)
    w.finalize()

