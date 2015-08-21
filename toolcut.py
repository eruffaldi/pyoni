

def strip(args,action,a,b):
    # scan all and keep pre and last
    if action == "stripcolor":
        id = 1
    else:
        id = 2
    while True:
            h = oni.readrechead(a)
            if h is None:
                    break
            prelast = last
            last = h
            if h["nid"] > mid:
                    mid = h["nid"]
            if h["nid"] == id:                
                if h["rt"] == oni.RECORD_SEEK_TABLE: # skip
                    break
                    #st = loadseek(a,h)
                    print "seek loaded and skipped, needs update"
                    a.seek(h["nextheader"],0) #h["fs"]-HEADER_SIZE+h["ps"],1)
                    continue
                oni.writehead(b,h)
                d = a.read(h["ps"]+h["fs"]-oni.HEADER_SIZE)
                b.write(d)
                # TODO recompute seek table
                if h["rt"] == oni.RECORD_NEW_DATA:
                    pd = oni.parsedatahead(a,h)
                    print pd["frameid"],h["ps"]
            if h["rt"] == oni.RECORD_END:
                oni.writeend(b)
                continue
            a.seek(h["nextheader"],0)
    needclose = True	

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

def skip(args,action,a):
    while True:
            h = oni.readrechead(a)
            if h is None:
                    break
            prelast = last
            last = h
            if h["nid"] > mid:
                    mid = h["nid"]
            if h["rt"] == oni.RECORD_SEEK_TABLE:
                # TODO gen seek
                pass
            elif h["rt"] == oni.RECORD_NODE_ADDED:
                hh = oni.parseadded(a,h)
                stats[h["nid"]].assignheader(h,hh) 
            elif h["rt"] == oni.RECORD_NEW_DATA:
                hh = oni.parsedatahead(a,h)
                q = stats[h["nid"]]
                if (q.oldframes % args.skipframes) == 0:
                    q.addframe(h,hh,b)
                    oni.copyblock(a,h,b,frame=q.newframes-1,timestamp=q.newtimestamp)
                q.oldframes += 1
            a.seek(h["nextheader"])
    needclose = True
    