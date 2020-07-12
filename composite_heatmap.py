import sys
import os
import math
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
# R. Redondo Jun 2020

# Input image
inputfile = str(sys.argv[1])
print('Processing ' + inputfile)
im = np.array(Image.open(inputfile), dtype=np.float32)
im = im[:,:,:3]
filename = os.path.basename(inputfile)
name, ext = os.path.splitext(filename)
path = os.path.split(inputfile)[0]

# Heatmap
files = os.listdir(path)
heatmap_filename = [s for s in files if name in s and 'heatmap' in s and 'heatmap' not in name]
if not heatmap_filename:
    print('Heatmap not found')
    sys.exit()

heatmap_filename = heatmap_filename[0]

print('Found heatmap file (' + path  + ') ' +  heatmap_filename)
heatmap_file = os.path.join(path, heatmap_filename)
hmap = np.array(Image.open(heatmap_file), dtype=np.float32)
hmap = hmap[:,:,:3]

# Step heatmaps
tmp = os.path.join(path, 'tmp')
try:
    os.mkdir(tmp)
except OSError:
    print ("Creation of the directory %s failed" % tmp)

steps = 10# 25
opacity = 0.7
cm = plt.get_cmap('viridis_r') # reverse colormap
graymap = cm(hmap.astype(float)/255)

for s in range(0, steps+1):

    mask = np.array(graymap[:,:,1,1])
    th = math.pow(float(s) / steps, 0.85)
    mask[mask < th] = 0
    mask[mask > 0] = 1

    mask = np.repeat(mask[:,:,np.newaxis], 3, axis=2)
    composite = im * mask + (hmap * opacity + im * (1- opacity)) * (1 - mask) 

    output = Image.fromarray(composite.astype(np.uint8))
    # output = output.resize([1000,712])

    comp_name = os.path.join(tmp, name + '_{:0>2d}'.format(s) + '.png')
    output.save(comp_name)
    print('Saved step ' + comp_name)
    comp_name = os.path.join(tmp, name + '_{:0>2d}'.format(2*steps-s+1) + '.png')
    output.save(comp_name)
    print('Saved step ' + comp_name)

print('Processing frames...')
framenames = os.path.join(tmp, name)
gifname = os.path.join(path, name + '.gif')
os.system('convert -delay 20 -loop 0 -fuzz 5% -layers Optimize ' + framenames + '*png ' + gifname)
print('Saved GIF ' + gifname)