
import os, shutil, glob
import time
import filecmp
from PIL import Image

class PhotoCatalog:   
   
     
    def __init__ (self, baseTargetDir):
        self.baseTargetDir = baseTargetDir
  
    def getFileDate(self, filename):
        y = '0'
        m = '0'
        segments = filename.split("_")
        if len(segments) > 1:
            if segments[0].lower() == "img":
                dateSegment = segments[1]
            else:
                dateSegment = segments[0]
            if len(dateSegment) == 8 and dateSegment.isdigit():
                y= dateSegment[0:4]
                m=dateSegment[4:6]
        else:
            segments = filename.split("-")
            if segments[0]=='video':
                filename = filename[6:]
            filename = filename[0:10]
            segments = filename.split("-")
            if len(segments) == 3:
               y= segments[0]
               m=segments[1]

        if int(m) > 12 or int(y) < 2000:
            return '0','0'

        return y,m

    def getExifDate(self,filename):
        try:
          dates = None
          obj = Image.open(filename)._getexif()
          if obj != None:
              dates = obj.get(36867,None)
        except AttributeError:
            pass
        except FileNotFoundError:
            print ("file not found: " + filename)
        if dates != None and len(dates) >= 10:
            segments = dates[0:10].split(":")
            if len(segments) == 3:
                #print("EXIF date : {0}, {1} for : {2}".format(segments[0], segments[1], filename))
                return segments[0], segments[1]
        return '0','0'

    months = {
       '01' : 'styczen',
       '02' : 'luty',
       '03' : 'marzec',
       '04': 'kwiecien',
       '05' : 'maj',
       '06' : 'czerwiec',
       '07' : 'lipiec',
       '08' : 'sierpien',
       '09' : 'wrzesien',
       '10' : 'pazdziernik',
       '11' : 'listopad',
       '12' : 'grudzien'
              }

    def getTargetFolder(self, year, month, filename):
        try:
           folder = self.baseTargetDir + year + "/" + self.months[month]
           if not os.path.exists(folder):
               os.makedirs(folder)
           return folder + "/" + filename           
        except KeyError:
           print (filename)
           return None


    def processFilename(self, filename):
         if os.path.isdir(filename) and not os.listdir(filename):
             print("removing empty dir: " + filename)
             os.rmdir(filename)
         y,m = self.getFileDate(os.path.basename(filename))
         if y=='0' and m=='0' and filename.lower().endswith(( ".jpg", ".png", ".jpg")):
             y,m = self.getExifDate(filename)
         if y != '0' and m != '0':
             target = self.getTargetFolder(y,m, os.path.basename(filename))
             print (filename + " -->" + target)
             if not os.path.isfile(target):
               os.rename(filename, target)
             elif  filecmp.cmp(filename, target, shallow = False):
               print("overwriting duplicate " + target)
               os.rename(filename, target)
             else:
               target = self.getTargetFolder(y,m, os.path.basename(filename) + str(time.time()) + os.path.basename(filename))
               if not os.path.isfile(target):
                 os.rename(filename,target)
                 print("renamed file to avoid conflicts: " + target)
               else:
                 print("File exists!: " + target)

    def processRecursive(self, folder):
        for filename in glob.iglob(folder + '**/*', recursive=True):
        #for root, dirnames, filenames in os.walk(folder):
            if "@eaDir" not in filename:
                print(filename)
                self.processFilename(filename)

    def processOneFolder(self, folder):
        os.chdir(folder)
        for filename in os.listdir(folder):           
            self.processFilename(filename)

    def clearEmptyFolders(self,folder):
        for filename in glob.iglob(folder + '**/', recursive=True):
            if os.path.isdir(filename) and "@eaDir" not in filename:
                if not os.listdir(filename):
                  print("removing empty dir: " + filename)
                  os.rmdir(filename)


c = PhotoCatalog("/photo/Albumy/")
for y in range(2000,2030):
    folder = "/photo/Albumy/" + str(y) + "/"
    if os.path.exists(folder):
        c.processOneFolder(folder)
