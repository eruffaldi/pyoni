
def fix(args,action,a):
        while True:
                h = oni.readrechead(a)
                if h is None:
                        break
                prelast = last
                last = h
                if h["nid"] > mid:
                        mid = h["nid"]
                elif h["rt"] == oni.RECORD_NEW_DATA:
                    hh = oni.parsedatahead(a,h)
                    q = stats[h["nid"]]
                    q.addframe(h,hh)
                # next record
                a.seek(h["nextheader"]) #h["fs"]-HEADER_SIZE+h["ps"]+pt,0)                
        if True:
            print "prelast",prelast
            print "last",last
            print "maxnodeid",mid

        if not last["nextheader"] <= filesize:
            print "last ends at",last["nextheader"],"with file size",filesize,"delta:",last["nextheader"]-filesize," we need truncate at pre last",prelast["afteroffset"]
            if action == "fixcut":
                a.truncate(prelast["nextheader"])
            last = prelast
            needclose = True

        if last["rt"] != oni.RECORD_END:
            print "missing RECORD_END. Last Record is:",last["rt"],"appending"
            if action == "fixcut":
                a.seek(0,2)
                oni.writeend(a)
                needclose = True

        if h0["maxnid"] != mid:
            print "bad maxnid",h0["maxnid"],"vs",mid,"fixing"
            h0["maxnid"] = mid
            if action == "fixcut":
                a.seek(0,0)
                oni.writehead1(a,h0)
                needclose = True
        else:
            print "header ok, no changes"
