import os

os.chdir('../my_images/egor')
for root, dirs, files in os.walk("."):
    for filename in files:
        print(filename)
