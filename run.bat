@echo off

set SRC=c:\dropbox\Camera Uploads
set DST=%USERPROFILE%\Desktop

cd c:\dropbox\private\github\mediaworker

python mediaworker.py photo,video "%SRC%" "%DST%\media"
python file2exif.py "%SRC%"
python mediaworker.py photo "%SRC%" "%DST%\media"