#!/bin/bash
echo "Rescaling"
pyonitool.py $1 --output $2a.rescale.oni --rescale 10 > $2a.rescale.txt
echo "Strip Color"
pyonitool.py $1 --output $2a.stripcolor.oni --stripcolor > $2a.stripcolor.txt
echo "Fix Cut"
pyonitool.py $1 --output $2a.fixcut.oni --fixcut > $2a.fixcut.txt
echo "Skip frames"
pyonitool.py $1 --output $2a.skip2.oni --skipframes 2 > $2a.skip2.txt
echo "Dup frames"
pyonitool.py $1 --output $2a.dup2.oni --dupframes 2 > $2a.dup2.txt
echo "Info"
pyonitool.py $1 --info > $2a.info.txt
echo "Dump"
pyonitool.py $1 --dump > $2a.dump.txt
echo "Checkcut"
pyonitool.py $1 --checkcut > $2a.check.txt
echo "Times"
pyonitool.py $1 --times > $2a.times.txt
echo "Extract Color"
pyonitool.py $1 --output $2a.mjpeg --mjpeg > $2a.mjpeg.txt
echo "Extract Depth"
pyonitool.py $1 --extractdepth qd

