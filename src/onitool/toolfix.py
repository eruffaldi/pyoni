from . import onifile as oni
import kinect1 as device
import struct
from collections import defaultdict

def fixnite(args,action,a,b):
    r = oni.Reader(a)
    w = oni.Writer(b,r.h0)
    if args.noseek:
        w.noseek = True
    ctargetnid = None
    ctargetnid2 = None
    emitted = False
    emitted2 = False
    foundprop = set()
    foundprop2 = set()
    neededprop = device.niteprops()
    neededprop.update(dict(IsFrameBased=1,IsPixelBased=1,IsStream=1,FrameSync=1,xnIsGenerating=1))
    neededprop2 = dict(IsFrameBased=1,IsPixelBased=1,IsStream=1,FrameSync=0,xnIsGenerating=1)
    if args.registered != -1:
        neededprop["RegistrationType"] = args.registered
        #XN_STREAM_PROPERTY_REGISTRATION_TYPE = 0x10801005, // "RegistrationType"
    print "fixing props",neededprop
    while True:
        h = r.next()
        if h is None:
            break
        if ctargetnid is not None and h["nid"] != ctargetnid and not emitted:
            # inject ParamCoeff = 4 for depth
            for k,v in neededprop.iteritems():
                if k in foundprop:
                    print "already present",k
                else:
                    print "adding property",k
                    if k == "ZPPS" or k == "LDDIS":
                        w.addprop(ctargetnid,k,oni.RECORD_REAL_PROPERTY,v)                        
                    elif k == "S2D":
                        n = device.S2D().tostring()
                        if len(n) != 4096: # 
                            print "ERROR! in S2D"
                            sys.exit(0)
                        w.addprop(ctargetnid,k,oni.RECORD_GENERAL_PROPERTY,n)
                    elif k == "D2S":
                        n = device.D2S().tostring()
                        if len(n) != 20002:
                            print "ERROR! in S2D"
                            sys.exit(0)
                        w.addprop(ctargetnid,k,oni.RECORD_GENERAL_PROPERTY,n)
                    else:
                        w.addprop(ctargetnid,k,oni.RECORD_INT_PROPERTY,v)
            #XN_STREAM_PROPERTY_S2D_TABLE S2D GENERAL 4096
            #XN_STREAM_PROPERTY_D2S_TABLE D2S GENERAL 20002
            emitted = True
        if ctargetnid2 is not None and h["nid"] != ctargetnid2 and not emitted2:
            # inject ParamCoeff = 4 for depth
            for k,v in neededprop2.iteritems():
                if k in foundprop2:
                    print "already present",k
                else:
                    print "adding property",k
                    w.addprop(ctargetnid2,k,oni.RECORD_INT_PROPERTY,v)
            #XN_STREAM_PROPERTY_S2D_TABLE S2D GENERAL 4096
            #XN_STREAM_PROPERTY_D2S_TABLE D2S GENERAL 20002
            emitted2 = True        
        if ctargetnid == h["nid"] and h["rt"] == oni.RECORD_INT_PROPERTY:
            p = oni.parseprop(a,h)
            if args.registered != -1 and p["name"] == "RegistrationType":
                print "replacing existing RegistrationType"
                w.addprop(ctargetnid,p["name"],oni.RECORD_INT_PROPERTY,args.registered)                            
            else:
                w.copyblock(h,a)
            foundprop.add(p["name"])
        elif ctargetnid == h["nid"] and h["rt"] == oni.RECORD_GENERAL_PROPERTY:
            p = oni.parseprop(a,h)
            foundprop.add(p["name"])
            w.copyblock(h,a)
        elif ctargetnid2 == h["nid"] and h["rt"] == oni.RECORD_INT_PROPERTY:
            p = oni.parseprop(a,h)
            foundprop2.add(p["name"])
            w.copyblock(h,a)
        elif h["rt"] == oni.RECORD_NODE_ADDED:
            hh = oni.parseadded(a,h)
            if hh["nodetype"] == oni.NODE_TYPE_DEPTH:
                ctargetnid = h["nid"]
                print "found depth",ctargetnid
            elif hh["nodetype"] == oni.NODE_TYPE_IMAGE:
                ctargetnid2 = h["nid"]
                print "found color",ctargetnid2
            w.copyblock(h,a)
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
            w.emitseek(h["nid"]) # we are changing props
        else:
            w.copyblock(h,a)
    w.finalize()


def makeregistered(args,action,a,b):
    r = oni.Reader(a)
    w = oni.Writer(b,r.h0)
    if args.noseek:
        w.noseek = True
    ctargetnid = None
    emitted = False
    foundprop = set()
    neededprop = {}
    already = False
    neededprop["RegistrationType"] = 2 # default
    if args.registered != -1:
        neededprop["RegistrationType"] = args.registered
    while True:
        h = r.next()
        if h is None:
            break
        if ctargetnid is not None and h["nid"] != ctargetnid and not emitted:
            # inject ParamCoeff = 4 for depth
            for k,v in neededprop.iteritems():
                if k in foundprop:
                    print "already present",k
                else:
                    print "adding property",k,"as",neededprop["RegistrationType"]
                    w.addprop(ctargetnid,k,oni.RECORD_INT_PROPERTY,v)
            emitted = True
        if ctargetnid == h["nid"] and h["rt"] == oni.RECORD_INT_PROPERTY:
            p = oni.parseprop(a,h)
            if p["name"] == "RegistrationType":
                print "replacing existing RegistrationType ",p["data"], " with ",neededprop["RegistrationType"]
                w.addprop(ctargetnid,p["name"],oni.RECORD_INT_PROPERTY,neededprop["RegistrationType"],datalen=p["datalen"])
                already = True
            else:
                w.copyblock(h,a)
            foundprop.add(p["name"])
        elif h["rt"] == oni.RECORD_NODE_ADDED:
            hh = oni.parseadded(a,h)
            if hh["nodetype"] == oni.NODE_TYPE_DEPTH:
                ctargetnid = h["nid"]
                print "found depth",ctargetnid
            w.copyblock(h,a)
        elif h["rt"] == oni.RECORD_SEEK_TABLE:
            if already: # needed for compare
                w.emitseek(h["nid"],a,h)
            else:
                w.emitseek(h["nid"])
        else:
            w.copyblock(h,a)
    w.finalize()

def fix(args,action,a):
    r = oni.Patcher(a)
    last = None
    prelast = None	
    mid = -1
    needclose = False
    print "fileheader",r.h0
    while True:
        h = r.next()
        if h is None:
            break
        elif h.magic != oni.magic:
            break
        elif h["rt"] == oni.RECORD_NEW_DATA:
            break
        if mid < h["nid"]:
            mid = h["nid"]
        prelast = last
        last = h
        if h["rt"] == oni.RECORD_NEW_DATA:
            hh = oni.parsedatahead(a,h)
            q = r.stats[h["nid"]]
            q.addframe(h,hh)
           
    if True:
        print "prelast",prelast
        print "last",last
        print "maxnodeid",mid

    if not last["nextheader"] <= filesize:
        print "FIXER last ends at",last["nextheader"],"with file size",filesize,"delta:",last["nextheader"]-filesize," we need truncate at pre last",prelast["afteroffset"]
        if action == "fixcut":
            a.truncate(prelast["nextheader"])
        last = prelast
        needclose = True

    if last["rt"] != oni.RECORD_END:
        print "FIXER missing RECORD_END. Last Record is:",last["rt"],"appending"
        if action == "fixcut":
            a.seek(0,2)
            oni.writeend(a)
            needclose = True

    if h0["maxnid"] != mid:
        print "FIXER bad maxnid",h0["maxnid"],"vs",mid,"fixing"
        h0["maxnid"] = mid
        if action == "fixcut":
            a.seek(0,0)
            oni.writehead1(a,h0)
            needclose = True
    else:
        print "header ok, no changes"
    if needclose:
    	a.finalize()
