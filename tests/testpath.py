import os
file_path = "/gpfs/bsc_home/xpliu/inference/README.md"
(filepath,tempfilename) = os.path.split(file_path)
(filename,extension) = os.path.splitext(tempfilename)
print(filepath)
print(tempfilename)
print(extension)

ok = os.path.splitext(tempfilename)
print(ok)