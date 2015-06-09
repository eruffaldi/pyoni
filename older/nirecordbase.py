#http://www.openni.org/wp-content/doxygen/html/classopenni_1_1_device.html
#https://github.com/leezl/OpenNi-Python/blob/master/testPythonOpenni.py
#https://github.com/leezl/OpenNi-Python/blob/master/primesense/openni2.py
from primesense import openni2
import os,time,datetime
import signal
import sys


def signal_handler(signal, frame):
	print 'You pressed Ctrl+C!'
	rec.stop()
	depth_stream.stop()
	color_stream.stop()
	openni2.unload()
	sys.exit(0)

if __name__ == "__main__":
	myni = os.environ.get("MYNI",".")

	openni2.initialize(myni)     # can also accept the path of the OpenNI redistribution

	now = datetime.datetime.now()
	iso_time = now.strftime("%Y-%m-%dT%H_%M_%S_%f")

	dev = openni2.Device.open_any()
	dev.set_depth_color_sync_enabled(True)
	print dev.get_sensor_info(openni2.SENSOR_DEPTH or openni2.SENSOR_COLOR)

	#tuple_time = time.strptime("2004-06-03T00:44:35", "%Y-%m-%dT%H:%M:%S")
	#t = time.time() 

	rec = openni2.Recorder("..\\..\\..\\myfilename " + iso_time + ".oni")

	depth_stream = dev.create_depth_stream()
	#depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX = 640, resolutionY = 480, fps = 30))
	depth_stream.start()

	color_stream = dev.create_color_stream()
	#color_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX = 640, resolutionY = 480, fps = 30))
	color_stream.start()
	
	print dev.get_sensor_info(openni2.SENSOR_COLOR)
	print dev.get_sensor_info(openni2.SENSOR_DEPTH)
	print dev.get_device_info()
	print color_stream.get_video_mode()
	print depth_stream.get_video_mode()

	rec.attach(depth_stream)
	rec.attach(color_stream,allow_lossy_compression =True)
	rec.start()

	#signal.signal(signal.CTRL_C_EVENT, signal_handler)
	signal.signal(signal.SIGINT, signal_handler)
	print 'Press Ctrl+C to quit'

	if True:
		dframe = depth_stream.read_frame()
		t = time.time()
		print "FirstSync:",t,dframe.frameIndex
		while True:
			time.sleep(1)		
	else:
		t = time.time()
		while True:
			pt = time.time()
			dframe = depth_stream.read_frame()
			dt = pt-t
			if dt == 0:
				dt = 1
			print 1.0/dt,dframe.frameIndex
			t = pt
			#cframe = color_stream.read_frame()
			#dframe_data = dframe.get_buffer_as_uint16()
			#cframe_data = cframe.get_buffer_as_uint8()

