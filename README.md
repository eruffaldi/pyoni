# pyoni
Pure python tool for manipulating OpenNI recorded files (oni). This tool supports extraction of data, time rescaling and fix of broken files.

Options
=======================

usage: pyonitool.py [-h] [--info] [--times] [--seeks] [--dump] [--copy]
                    [--rescale RESCALE] [--fixcut] [--checkcut]
                    [--dupframes DUPFRAMES] [--stripcolor] [--stripdepth]
                    [--stripir] [--registercolor] [--registerdepth] [--mjpeg]
                    [--extractcolor EXTRACTCOLOR]
                    [--extractdepth EXTRACTDEPTH] [--extractir EXTRACTIR]
                    [--fseek FSEEK] [--fduration FDURATION]
                    [--skipframes SKIPFRAMES] [--coloreddepth]
                    [--output OUTPUT] [--cutbytime CUTBYTIME]
                    [--cutbyframe CUTBYFRAME]
                    file

Scan OpenNI ONI files

positional arguments:
  file                  ONI filename

optional arguments:
  -h, --help            show this help message and exit
  --info
  --times               print times of each frame
  --seeks               print seeks
  --dump
  --copy                simply copies the content of the ONI via parsing
                        (rebuilds the seektable only)
  --rescale RESCALE     rescale timings
  --fixcut              fixes cut file NOT TESTED HERE
  --checkcut            checks if file was cut NOT TESTED HERE
  --dupframes DUPFRAMES
                        duplicate frames
  --stripcolor
  --stripdepth
  --stripir             removes IR
  --registercolor       registers color over depth
  --registerdepth       registers depth over color
  --mjpeg               extract the color stream as motion jpeg
  --extractcolor EXTRACTCOLOR
                        extract the color stream single jpeg or png images.
                        This option specifies the target path, numbering is
                        the frame number
  --extractdepth EXTRACTDEPTH
                        extract the depth stream single png images. This
                        option specifies the target path, numbering is the
                        frame number
  --extractir EXTRACTIR
                        extract the depth stream single png images. This
                        option specifies the target path, numbering is the
                        frame number
  --fseek FSEEK         seek frame for extract
  --fduration FDURATION
                        duration of extraction in frames
  --skipframes SKIPFRAMES
                        skip n frames
  --coloreddepth        colored depth
  --output OUTPUT
  --cutbytime CUTBYTIME
                        cut by specifing time in seconds:
                        startseconds,endseconds
  --cutbyframe CUTBYFRAME
                        cut by specifing time in frames: startframe,endframe

  
Build
=======================

Two C++ codes require manual steps (for the moment):
- xn16zdec.cpp
- anyregistration.cpp

References
=======================

https://github.com/OpenNI/OpenNI2/blob/master/Source/Drivers/OniFile/DataRecords.cpp
https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniRecorder.cpp
https://github.com/OpenNI/OpenNI2/blob/master/Source/Core/OniDataRecords.cpp
CODECS: https://github.com/OpenNI/OpenNI2/blob/5b88c95e4f8d19b95713e3c873c7d07e48e5605b/Source/Drivers/OniFile/Formats/Xn16zEmbTablesCodec.h
https://github.com/OpenNI/OpenNI2/blob/5b88c95e4f8d19b95713e3c873c7d07e48e5605b/Source/Drivers/OniFile/Formats/XnStreamCompression.cpp
