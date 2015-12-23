



python setup.py sdist bdist upload -r pypi 
python setup.py build --compiler=mingw32 bdist_wininst upload -r pypi 

#twine upload -r pypi -s dist/pyoni-0.5.win32-py2.7.exe dist/pyoni-0.5-py2.7-macosx-10.10-intel.egg