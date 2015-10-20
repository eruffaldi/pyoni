w = [x.strip() for x in "fx, fy, cx, cy, k1, k2, k3, p1, p2".split(",")]
for x in w:
	print "depth_p.%s = depth_%s;" % (x,x)

cc ="""
    float fx, fy, cx, cy;

    float shift_d, shift_m;

    float mx_x3y0; // xxx
    float mx_x0y3; // yyy
    float mx_x2y1; // xxy
    float mx_x1y2; // yyx
    float mx_x2y0; // xx
    float mx_x0y2; // yy
    float mx_x1y1; // xy
    float mx_x1y0; // x
    float mx_x0y1; // y
    float mx_x0y0; // 1

    float my_x3y0; // xxx
    float my_x0y3; // yyy
    float my_x2y1; // xxy
    float my_x1y2; // yyx
    float my_x2y0; // xx
    float my_x0y2; // yy
    float my_x1y1; // xy
    float my_x1y0; // x
    float my_x0y1; // y
    float my_x0y0; // 1
"""
for l in cc.split("\n"):
	l = l.split(";")[0].strip();
	if len(l) == 0:
		continue
	l = l.split("float")[1].strip();
	w = [x.strip() for x in l.split(",")]
	for x in w:
		print "rgb_p.%s = color_%s;" % (x,x)