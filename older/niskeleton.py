"""OpenNI Capture with External Data Sync"""

__author__      = "Emanuele Ruffaldi"
__copyright__   = "Copyright 2013, Scuola Superiore Sant'Anna PERCRO"

#Required: https://pypi.python.org/pypi/primesense/
#https://github.com/leezl/OpenNi-Python/blob/master/primesense/openni2.py
#See: https://github.com/futureneer/openni2-tracker/blob/master/src/tracker.cpp
#http://www.primesense.com/wp-content/uploads/2013/04/PrimeSense_NiTE2API_ProgTutorialGuide_C++Samples_docver0.2.pdf
#http://www.nsl.tuis.ac.jp/svn/vc++/JunkBox_Lib++/branches/for_Rinions-3.4/NiLib/OpenNi2Device.cpp
#
# See Also: http://doc.instantreality.org/tutorial/using-openni-devices/

from primesense import openni2,nite2,_nite2
import os,time,datetime,signal,sys,socket

def signal_handler(signal, frame):
	print 'You pressed Ctrl+C. Closing logger and device'
	openni2.unload()
	sys.exit(0)

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description='Automatic Storage of NI content in OpenNI format')
	parser.add_argument('--input', required=True,help="inputfile")

	args = parser.parse_args()
	
	myni = os.environ.get("MYNI",".")

	try:
		openni2.initialize(myni)     # can also accept the path of the OpenNI redistribution
	except:
		print "cannot initialize OpenNI2. The OpenNI2 Redist directory should be in the PATH. Use the MYNI environment variable"
		raise 

	try:
		nite2.initialize(myni)
	except:
		print "cannot initialize Nite2"
		raise 

	dev = openni2.Device.open_file(args.input)
	print dev.get_sensor_info(openni2.SENSOR_COLOR)
	print dev.get_sensor_info(openni2.SENSOR_DEPTH)

	print dev.get_device_info()
	depth_stream = dev.create_depth_stream()
	depth_stream.start()

	color_stream = dev.create_color_stream()
	color_stream.start()

	print color_stream.get_video_mode()
	print depth_stream.get_video_mode()
	#Device::getPlaybackControl()
	#PlaybackControl::setRepeatEnabled()
	#PlaybackControl::setSpeed() 
	#PlaybackControl::seek()
	# PlaybackControl::getNumberOfFrames()

	ps = dev.playback

	ps.set_repeat_enabled(True)
	print "Depth Frames",ps.get_number_of_frames(depth_stream)
	"""
	"""
	
	# NOT WORKING WITH FILE... MAYBE
	ut = nite2.UserTracker(dev)

	while True:
		utf = ut.read_frame()
		for u in utf.users:
			if u.is_new():
				print "new user",u.id,utf.timestamp
				ut.start_skeleton_tracking(u.id)	
			elif u.is_visible():
				# get skeleton get joint
				sk = u.skeleton
				jh = sk.joints[_nite2.NiteJointType.NITE_JOINT_HEAD]
				print utf.timestamp,jh.position

#userTrackerFrame.getUsers();
#updateUserState(user,userTrackerFrame.getTimestamp());
#isNew
# const nite::UserData& user = users[i];
# userTracker.startSkeletonTracking(user.getId());
#else if (user.getSkeleton().getState() == nite::SKELETON_TRACKED)
#const nite::SkeletonJoint& head = user.getSkeleton().getJoint(nite::JOINT_HEAD);
#if (head.getPositionConfidence() > .5)
#printf("%d. (%5.2f, %5.2f, %5.2f)\n", user.getId(), head.getPosition().x, head.getPosition().y, head.getPosition().z);




