import glob
import os
import re
import shutil
import subprocess
import sys
import time

from multiprocessing import Queue, Process
from queue import Empty

# Defines
DTORIG = "Exif.Photo.DateTimeOriginal"
DTDIG = "Exif.Photo.DateTimeDigitized"
DTDIG2 = "Xmp.exif.DateTimeDigitized"
DT = "Exif.Image.DateTime"

# Configuration
OPERATION = "move"
PHOTO = "photos"
PHOTODST = "%Y/%m - %b/%Y-%m-%d_%H%M%S"
PHOTOMASK = "jpg"
VIDEO = "videos"
VIDEODST = "%Y/%m - %b/%Y-%m-%d_"
VIDEOMASK = "mov,avi,mp4"

class photo:
    def __init__(self, src, dst, queue):
        self.queue = queue
        self.recurse(src, dst)

    def getexif(self, path):
        exifdata = {}

        for ext in PHOTOMASK.split(","):
            pipe = subprocess.Popen("exiv2.exe -PEIXkt \"%s\\*.%s\"" % (path, ext), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
            if pipe != None:
                lines = pipe.read().decode("UTF-8")
                for line in lines.split("\n"):
                    if "DateTime" in line:
                        for i in [DTORIG, DTDIG, DTDIG2, DT]:
                            if i in line:
                                match = [j.strip() for j in line.split(i)]
                                if match[0] not in exifdata.keys():
                                    exifdata[match[0]] = {}

                                try:
                                    exifdata[match[0]][i] = time.strptime(match[1], "%Y:%m:%d %H:%M:%S")
                                except:
                                    print("Error with %s format" % match[1].strip())

        return exifdata

    def process(self, exifdata, dst):
        for f in exifdata.keys():
            tag = None
            for i in [DTORIG, DTDIG, DTDIG2, DT]:
                if i in exifdata[f].keys():
                    tag = i
                    break
            if tag != None:
                self.queue.put({
                    OPERATION: {
                        "src": f,
                        "dst": "%s/%s/%s" % (dst, PHOTO, time.strftime(PHOTODST, exifdata[f][tag]))
                    }
                })

    def recurse(self, src, dst):
        print("Processing %s" % printpath(src))

        exifdata = self.getexif(src)
        if exifdata != {}:
            self.process(exifdata, dst)

        for path in glob.iglob("%s/*" % src):
            if os.path.isdir(path):
                time.sleep(0.05)
                self.recurse(path, dst)

class video:
    def __init__(self, src, dst, queue):
        self.queue = queue
        self.recurse(src, dst)

    def getdate(self, path):
        datedata = {}

        exts = ["." + i.lower() for i in VIDEOMASK.split(",")]
        for vid in glob.iglob("%s/*" % path):
            root, ext = os.path.splitext(vid)
            if ext.lower() in exts:
                statinfo = os.stat(vid)
                datedata[vid] = statinfo.st_mtime

        return datedata

    def process(self, datedata, dst):
        for f in datedata.keys():
            self.queue.put({
                OPERATION: {
                    "src": f,
                    "dst": "%s/%s/%s" % (dst, VIDEO, time.strftime(VIDEODST, time.localtime(datedata[f])))
                }
            })

    def recurse(self, src, dst):
        print("Processing %s" % printpath(src))

        datedata = self.getdate(src)
        if datedata != {}:
            self.process(datedata, dst)

        for path in glob.iglob("%s/*" % src):
            if os.path.isdir(path):
                time.sleep(0.05)
                self.recurse(path, dst)

class rmdir:
    def __init__(self, src, pattern, queue):
        self.queue = queue
        self.pattern = pattern.split(",")
        self.recurse(src)

    def process(self, path):
        self.queue.put({
            "rmdir": {
                "src": path
            }
        })

    def recurse(self, src):
        print("Processing %s" % printpath(src))

        basename = os.path.basename(src)
        if basename in self.pattern:
            self.process(src)
            return

        for path in glob.iglob("%s/*" % src):
            if os.path.isdir(path):
                time.sleep(0.05)
                self.recurse(path)

        for path in glob.iglob("%s/.*" % src):
            if os.path.isdir(path):
                time.sleep(0.05)
                self.recurse(path)

class processor:
    def __init__(self):
        self.queue = Queue()
        self.child = Process(target=self.process)
        self.child.start()

    def getqueue(self):
        return self.queue

    def process(self):
        while True:
            try:
                job = self.queue.get(block=False)
                if job == None:
                    break

                for key in job.keys():
                    eval('self.%s(job["%s"])' % (key, key))
            except Empty:
                time.sleep(0.05)
            except:
                print("Error with job: %s" % job)
                continue

    def copy(self, job, move=False):
        src = job["src"]
        dst = job["dst"]

        name, ext = os.path.splitext(src)

        try:
            os.makedirs(os.path.dirname(dst))
        except:
            pass

        i = 1
        unique = "-" + i.__str__()
        while os.path.isfile(dst + unique + ext):
            i += 1
            unique = "-" + i.__str__()

        dst = dst + unique + ext

        if move == True:
            print("Moving %s" % printpath(src))
        else:
            print("Copying %s" % printpath(src))

        print("    ==> %s" % printpath(dst))

        try:
            if move == True:
                shutil.move(src, dst)
            else:
                shutil.copy2(src, dst)
        except:
            return False

        return True

    def move(self, job):
        return self.copy(job, move=True)

    def rmdir(self, job):
        src = job["src"]

        print("Deleting %s" % printpath(src))

        try:
            shutil.rmtree(src)
        except:
            return False

        return True

def help():
    print("Syntax: mediaworker photo,video <srcdir> <dstdir>")
    print("Syntax: mediaworker rmdir <srcdir> <pattern1,pattern2>")

def fixdir(d):
    d = d.replace("\\", "/")
    while d[-1] == "/": d = d[:-1]

    return d

def printpath(path, length=70):
    if len(path) > length: pathprint = "~" + path[len(path)-length:]
    else: pathprint = path

    return pathprint

if __name__ == '__main__':
    if len(sys.argv) != 4 or not os.path.isdir(sys.argv[2]):
        help()
    else:
        proc = processor()
        queue = proc.getqueue()

        src = fixdir(sys.argv[2])
        modes = sys.argv[1].split(",")
        for mode in modes:
            if mode in ["photo", "video"]:
                dst = fixdir(sys.argv[3])

                eval("%s(src, dst, queue)" % mode)
            elif mode == "rmdir":
                patt = sys.argv[3]

                eval("%s(src, patt, queue)" % mode)

        queue.put(None)
