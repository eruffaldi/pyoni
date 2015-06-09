# pyoni
Pure python tool for manipulating OpenNI recorded files (oni). This tool supports extraction of data, time rescaling and fix of broken files.

Options
=======================

usage: pyonitool.py [-h] [--info] [--times] [--rescale RESCALE] [--fixcut]
                    [--checkcut] [--stripcolor] [--mjpeg] [--dump]
                    [--output OUTPUT]
                    file

Scan OpenNI ONI files

positional arguments:
  file               ONI filename

optional arguments:
  -h, --help         show this help message and exit
  --info
  --times            print times of each frame
  --rescale RESCALE  rescale timings
  --fixcut           fixes cut file
  --checkcut         checks if file was cut
  --stripcolor
  --mjpeg            extract the color stream as motion jpeg
  --dump
  --output OUTPUT
  
Build
=======================

Use CMake or a simple (gcc --shared xn16zdec.cpp)

References
=======================

https://github.com/OpenNI/OpenNI2/blob/master/Source/Drivers/OniFile/DataRecords.cpp
https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniRecorder.cpp
https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniDataRecords.cpp
CODECS: https://github.com/OpenNI/OpenNI2/blob/5b88c95e4f8d19b95713e3c873c7d07e48e5605b/Source/Drivers/OniFile/Formats/Xn16zEmbTablesCodec.h
https://github.com/OpenNI/OpenNI2/blob/5b88c95e4f8d19b95713e3c873c7d07e48e5605b/Source/Drivers/OniFile/Formats/XnStreamCompression.cpp
