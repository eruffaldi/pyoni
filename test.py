#cap_openni2.cpp usa status = device.open(filename);
#cap_openni.cpp : status = context.OpenFileRecording( filename, productionNode );
import numpy as np
import cv2,sys
import cv2.cv as cv
cap = cv2.VideoCapture(sys.argv[1])

if True:
    print("Depth generator output mode:")
    print("FRAME_WIDTH      " + str(cap.get(cv.CV_CAP_PROP_FRAME_WIDTH)))
    print("FRAME_HEIGHT     " + str(cap.get(cv.CV_CAP_PROP_FRAME_HEIGHT)))
    print("FRAME_MAX_DEPTH  " + str(cap.get(cv.CV_CAP_PROP_OPENNI_FRAME_MAX_DEPTH)) + "mm")
    print("FPS              " + str(cap.get(cv.CV_CAP_PROP_FPS)))
    print("REGISTRATION     " + str(cap.get(cv.CV_CAP_PROP_OPENNI_REGISTRATION)) + "\n")

while(True):
    # Capture frame-by-frame
    cap.grab();
    
    if True:   
        frame = cap.retrieve( cv.CV_CAP_OPENNI_BGR_IMAGE )[1]
        depthMap = cap.retrieve( cv.CV_CAP_OPENNI_DEPTH_MAP );
    else:
        frame = cap.retrieve()[1]
    print frame
    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()