# ----------------
# Create a pbarray
# ----------------

import os
from time import time
from cStringIO import StringIO

import Image
import numpy

import pbarray_pb2
import pbarray as pb


def get_jpeg_string(array, quality=100):
    """Go from numpy array to jpeg string."""
    image = Image.fromarray(array)
    output = StringIO()
    image.save(output, format='JPEG', quality=quality)
    output.seek(0)
    string = output.read()
    return string


pbarray = PBArrayWriter('./pb')

# For each image
data_item = pbarray_pb2.DataItem()
meta_item = pbarray_pb2.MetaItem()

image_array = numpy.uint8(numpy.random.randint(255, size=(256, 256, 3)))

data_item.jpeg = get_jpeg_string(image_array)
meta_item.filename = 'test.jpeg'
meta_item.width, meta_item.height, _ = image_array.shape

for i in range(128):
    pbarray.Put(data_item, meta=meta_item)

tic = time()
pbarray.Close()
toc = time()
print 'Saving takes %0.6f sec.' % (toc-tic)

# --------------
# Read a pbarray
# --------------

from cStringIO import StringIO
import Image
import numpy
from pbarray import PBArray
pbarray = PBArray('./pb')

data = numpy.zeros((128, 256, 256, 3), dtype=numpy.uint8)
tic = time()

indices = numpy.arange(20000)
numpy.random.shuffle(indices)
for i, index in enumerate(indices[0:128]):
    data_item, meta_item = pbarray.Get(index)
    data[i, :, :, :] = numpy.array(Image.open(StringIO(data_item.jpeg)))
toc = time()
print 'Loading a batch takes %0.2f sec.' % (toc-tic)
