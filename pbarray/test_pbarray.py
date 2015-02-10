# ----------------
# Create a pbarray
# ----------------

import os
from time import time
import Image
import pbarray_pb2
import pbarray as pb

pbarray = pb.PBArrayWriter('./pb')

# For each image
data_item = pbarray_pb2.DataItem()
meta_item = pbarray_pb2.MetaItem()

filepath = '/Users/badyokozuna/Desktop/test_image.jpg'
filename = os.path.basename(filepath)

with open(filepath, 'rb') as f:
    data_item.jpeg = f.read()
image = Image.open(filepath)
meta_item.filename = filename
meta_item.width, meta_item.height = image.size

for i in range(128):
    pbarray.Put(data_item, meta=meta_item)

tic = time()
pbarray.Write()
toc = time()
print 'Saving takes %0.2f sec.' % (toc-tic)

# --------------
# Read a pbarray
# --------------

from StringIO import StringIO
import Image
import numpy
from pbarray import PBArray
pbarray = PBArray('./pb')

data = numpy.zeros((128, 256, 256, 3), dtype=numpy.uint8)
tic = time()
for i in range(128):
    data_item, meta_item = pbarray.Get(i)
    data[i, :, :, :] = numpy.array(Image.open(StringIO(data_item.jpeg)))
toc = time()
print 'Loading a batch takes %0.2f sec.' % (toc-tic)
