import onifile as oni
import struct

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
