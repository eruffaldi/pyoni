#!/usr/bin/python
# OpenNI ONI tool
# by Emanuele Ruffaldi PERCRO-SSSA 2013-2015
#
# Implemented Operations:
# - time rescale
# - print times
# - fix truncated file
# - extract motion jpeg of color
# - remove color component
# - extract single image/depth
#
# Possible future:
# - IN PROGRESS split/cut
# - IN PROGRESS 
# - dump stats
#
# TODO: XN_STREAM_PROPERTY_S2D_TABLE
#
# Version 2015/06/18

import struct#
import onitool.onifile as oni
import shutil
import array
import sys
import onitool.toolext as toolext
try:
    import onitool.toolreg as toolreg
except:
    print sys.exc_info()
    toolreg =None
import onitool.toolinfo as toolinfo
import onitool.toolcut as toolcut
import onitool.tooltime as tooltime
import onitool.toolfix as toolfix
try:
    import onitool.toolreg as toolreg
except:
    toolreg = None
    print "missing dll for toolreg"


def interval(s,t,tt):
    try:
        x, y = map(tt, s.split(','))
        return x, y
    except:
        raise argparse.ArgumentTypeError("%s must be x,y" % t)

if __name__ == "__main__":
    import sys,os,argparse

    parser = argparse.ArgumentParser(description='Scan OpenNI ONI files')
    parser.add_argument('file',help='ONI filename')
    parser.add_argument('--info',action="store_true")
    parser.add_argument('--times',action="store_true",help="print times of each frame")
    parser.add_argument('--seeks',action="store_true",help="print seeks")
    parser.add_argument('--dump',action="store_true")
    parser.add_argument('--copy',action="store_true",help="simply copies the content of the ONI via parsing (rebuilds the seektable only)")
    parser.add_argument('--rescale',type=float,default=0.0,help="rescale timings")
    parser.add_argument('--fixcut',action="store_true",help="fixes cut file NOT TESTED HERE")
    parser.add_argument('--fixnite',action="store_true",help="fixes nite file NOT TESTED HERE")
    parser.add_argument('--checkcut',action="store_true",help="checks if file was cut NOT TESTED HERE")
    parser.add_argument('--dupframes',type=int,default=None,help="duplicate frames")
    parser.add_argument('--stripcolor',action="store_true")
    parser.add_argument('--stripdepth',action="store_true")
    parser.add_argument('--noseek',action="store_true",help="disable seek")
    parser.add_argument('--compare',help="compare another file")
    parser.add_argument('--extractframes',type=str,help="extract frames from the given file, requires,")
    parser.add_argument('--stripir',action="store_true",help="removes IR")
    parser.add_argument('--no-registersynctime',dest="registersynctime",action="store_false",help="no sync times while registering")
    parser.add_argument('--registercolor',action="store_true",help="registers color over depth (output is depth size)")
    parser.add_argument('--registerdepth',action="store_true",help="registers depth over color (output is color size, uses filter)")
    parser.add_argument('--mjpeg',action="store_true",help="extract the color stream as motion jpeg")
    parser.add_argument('--extractcolor',help="extract the color stream single jpeg or png images. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--extractdepth',help="extract the depth stream single png images. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--extractir',help="extract the depth stream single png images. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--fseek',type=int,default=0,help="seek frame for extract")
    parser.add_argument('--fduration',type=int,default=-1,help="duration of extraction in frames")
    parser.add_argument('--skipframes',type=int,default=None,help="skip n frames")
    parser.add_argument('--coloreddepth',action="store_true",help="colored depth")
    parser.add_argument('--makeregistered',action="store_true",help="fake reg")
    parser.add_argument('--registered',type=int,default=-1,help="registered modified for fixnite")
    parser.add_argument('--isregistered',action="store_true",help="check registered")
    parser.add_argument('--output',default=None)
    parser.add_argument('--outputdir')
    #parser.add_argument('--extractboth',help="extract the depth and color stream as png and jpeg respectively. This option specifies the target path, numbering is the frame number")
    parser.add_argument('--cutbytime',help="cut by specifing time in seconds: startseconds,endseconds",type=lambda x:interval(x,"time",float))
    parser.add_argument('--cutbyframe',help="cut by specifing time in frames: startframe,endframe",type=lambda x:interval(x,"frame",int))

    args = parser.parse_args()

    if args.file is None:
        print "Required: ONI filename"
        sys.exit(-1)

    action = ""
    patchaction = False



    if args.mjpeg:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "mjpeg"

    if args.rescale:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "rescale"

    if args.stripcolor:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "stripcolor"

    if args.stripdepth:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "stripdepth"

    if args.stripir:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "stripir"

    if args.fixcut :
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is not None:
            print "FIXCUT works in patch mode"
            sys.exit(-1)
        patchaction = True
        action = "fixcut"

    if args.makeregistered:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "FIXNITE requires output"
            sys.exit(-1)
        action = "makeregistered"

    if args.isregistered:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "isregistered"
    if args.fixnite :
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "FIXNITE requires output"
            sys.exit(-1)
        action = "fixnite"

    if args.copy:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "copy"

    if args.seeks:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is not None:
            print "Not Required output"
            sys.exit(-1)
        action = "seeks"

    if args.checkcut:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is not None:
            print "Not Required: ONI filename in output --output"
            sys.exit(-1)
        action = "checkcut"

    if args.cutbyframe is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        target = ("frame",args.cutbyframe)
        action = "cutbyframe"

    if args.cutbytime is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        target = ("timeus",[int(x*1E6) for x in args.cutbyframe])
        action = "cutbytime"

    if args.extractframes:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.outputdir == "":
            print "output dir needed for extractframes"
            sys.exit(-1)
        action = "extractframes"



    subaction = ""
    extractpath = ""
    varia = ['extractcolor','extractdepth','extractir'] #,'extractboth']
    for x in varia:
        if getattr(args,x):
            if action != "":
                print "Already specified action",action
                sys.exit(-1)
            subaction = x
            action = "extract"
            extractpath = getattr(args,x)
            print "extract action",extractpath

    if args.dump:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "dump"

    if args.info:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "info"

    if args.compare is not None:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "compare"

    if args.dupframes:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "dupframes"

    if args.skipframes:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        action = "skipframes"
    if args.registercolor:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "registercolor"
    if args.registerdepth:
        if action != "":
            print "Already specified action",action
            sys.exit(-1)
        if args.output is None:
            print "Required: ONI filename in output --output"
            sys.exit(-1)
        action = "registerdepth"

    filesize = os.stat(args.file).st_size
    if patchaction:
        shutil.copyfile(args.file,args.output)
        args.file = args.output
        print args.file
        a = open(args.file,"r+b")
    else:
        a = open(args.file,"rb")
        if action != "" and args.output is not None:
            b = open(args.output,"wb")

    if action == "registercolor" or action == "registerdepth":
        toolreg.register(args,action,a,b)
    elif action == "extract":
        toolext.extract(args,subaction,extractpath,a)        
    elif action == "isregistered":
        toolinfo.checkregistered(args,a)
    elif action == "mjpeg":
        toolext.extractmjpeg(args,a,b)        
    elif action == "stripcolor" or action == "stripir" or action == "stripdepth":
        toolcut.strip(args,action,a,b)
    elif action == "cutbyframe" or action == "cutbytime":
        toolcut.cut(args,target,a,b)
    elif action == "rescale":
        tooltime.rescale(args,args.rescale,a,b)
    elif action == "copy":
        toolcut.copy(args,a,b)
    elif action == "dupframes":
        toolcut.dupframes(args,a,b)
    elif action == "seeks":
        toolinfo.seeks(args,a)
    elif action == "skipframes":
        toolcut.skip(args,a,b)
    elif action == "fixcut" or action == "checkcut":
        toolfix.fix(args,action,a)
    elif action == "fixnite":
        toolfix.fixnite(args,action,a,b)
    elif action == "compare":
        toolinfo.compare(args,action,a,open(args.compare,"rb"))
    elif action == "makeregistered":
        toolfix.makeregistered(args,action,a,b)
        #args.registered = 2
        #toolfix.fixnite(args,action,a,b)
    elif args.times:
        toolinfo.times(args,a)
    elif action == "info":
        toolinfo.info(args,a)
    elif action == "extractframes":
        toolext.extractframes(args,a,[int(x) for x in open(args.extractframes,"r")],args.outputdir)
    elif action == "dump" or action == "":
        toolinfo.dump(args,a)
    else:
        print "unknown action",action

    if False:
        if needclose:
            # if need to close first PATCH the NODE ADDED
            # then patch the writeseek        
            for q in stats.values():
                print "writing",q
                q.patchframeheader(b)
                q.writeseek(b)
            h0["ts"] = max([q.maxts for q in stats.values()])
            oni.writehead1(b,h0)                           
        a.close()

