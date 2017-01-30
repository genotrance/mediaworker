import glob
import os
import subprocess
import sys
import time

# Syntax: python setdt.py path datestr
# Date format:  2017:01:16 19:00:13

# Defines
DTORIG = "Exif.Photo.DateTimeOriginal"
DTDIG = "Exif.Photo.DateTimeDigitized"
DTDIG2 = "Xmp.exif.DateTimeDigitized"
DT = "Exif.Image.DateTime"

if __name__ == "__main__":
	if len(sys.argv) != 3:
		sys.exit()

	for i in glob.glob(sys.argv[1] + "\\*.jpg"):
		tstr = sys.argv[2]

		print("Setting %s date to %s" % (i, tstr))
		os.system('exiv2.exe -M"set %s %s" -M"set %s %s" -M"set %s %s" "%s"' % (DTORIG, tstr, DTDIG, tstr, DT, tstr, i))