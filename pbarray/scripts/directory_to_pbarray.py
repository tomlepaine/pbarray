import os
from glob import glob
from time import time

import Image

from pbarray import pbarray_pb2
from pbarray import pbarray as pb

# TODO(tpaine) add argparse to make this into a real script.
dir = '/Users/badyokozuna/'
pattern = os.path.join(dir, '*', '*.jpeg')
jpeg_paths = glob(pattern)

pbarray = pb.PBArrayWriter('./pb')

print 'here'
for jpeg_path in jpeg_paths:
    print jpeg_path
    data_item = pbarray_pb2.DataItem()
    meta_item = pbarray_pb2.MetaItem()

    with open(jpeg_path, 'rb') as f:
        data_item.jpeg = f.read()
    image = Image.open(jpeg_path)
    filepath = os.path.relpath(jpeg_path, start=dir)
    meta_item.filename = filepath
    meta_item.width, meta_item.height = image.size

    pbarray.Put(data_item, meta=meta_item)

tic = time()
pbarray.Write()
toc = time()
print 'Saving takes %0.2f sec.' % (toc-tic)
