import glob
import os
import subprocess
import sys
import time

# Defines
DTORIG = "Exif.Photo.DateTimeOriginal"
DTDIG = "Exif.Photo.DateTimeDigitized"
DTDIG2 = "Xmp.exif.DateTimeDigitized"
DT = "Exif.Image.DateTime"

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit()

	for i in glob.glob(sys.argv[1] + "\\*.jpg"):
		flag = False
		pipe = subprocess.Popen("exiv2.exe -PEIXkt \"%s\"" % i, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
		if pipe != None:
			lines = pipe.read().decode("UTF-8")
			for line in lines.split("\n"):
				if "DateTime" in line:
					flag = True
		if not flag:
			t = time.localtime(os.stat(i).st_mtime)
			tstr = time.strftime("%Y:%m:%d %H:%M:%S", t)
			print("Setting %s date to %s" % (i, tstr))
			os.system('exiv2.exe -M"set %s %s" -M"set %s %s" -M"set %s %s" "%s"' % (DTORIG, tstr, DTDIG, tstr, DT, tstr, i))