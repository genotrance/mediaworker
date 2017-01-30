import os
import sys

def copy_utime(src, dst):
	if not os.path.exists(src):
		print("Source '%s' not found" % src)
		return
		
	if not os.path.exists(dst):
		print("Destination '%s' not found" % dst)
		return
		
	sstat = os.stat(src)
	
	os.utime(dst, (sstat.st_atime, sstat.st_mtime))
	
	dstat = os.stat(dst)
	
	print("Source = %d, %d" % (sstat.st_atime, sstat.st_mtime))
	print("Destination = %d, %d" % (dstat.st_atime, dstat.st_mtime))

if __name__ == "__main__":
	if len(sys.argv) == 3:
		copy_utime(sys.argv[1], sys.argv[2])