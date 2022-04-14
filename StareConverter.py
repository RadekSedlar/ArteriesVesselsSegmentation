from tkinter.tix import InputOnly
import DataPaths
from PIL import Image
import os
import glob

starePath = os.path.join(DataPaths.get_current_path(), "Data", "STARE")

print(f"DIRECTORY  {starePath}")

for infile in glob.glob(os.path.join(starePath, "*.ppm")):
    print(f"working on file {infile}")
    file, ext = os.path.splitext(infile)
    im = Image.open(infile)
    im.save(file + ".bmp", "BMP")
    im.close()
    os.remove(infile)
print("DONE ??????")

