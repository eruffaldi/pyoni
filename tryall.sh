#!/bin/bash
python pyonitool.py $1 --output $2a.rescale.oni --rescale 10 > $2a.rescale.txt
python pyonitool.py $1 --output $2a.stripcolor.oni --stripcolor > $2a.stripcolor.txt
python pyonitool.py $1 --output $2a.fixcut.oni --fixcut > $2a.fixcut.txt
python pyonitool.py $1 --output $2a.skip2.oni --skipframes 2 > $2a.skip2.txt
python pyonitool.py $1 --output $2a.dup2.oni --dupframes 2 > $2a.dup2.txt
python pyonitool.py $1 --info > $2a.info.txt
python pyonitool.py $1 --dump > $2a.dump.txt
python pyonitool.py $1 --checkcut > $2a.check.txt
python pyonitool.py $1 --times > $2a.times.txt
python pyonitool.py $1 --output $2a.mjpeg --mjpeg > $2a.mjpeg.txt

