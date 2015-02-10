import os

import numpy

import pbarray_pb2


class PBArrayWriter(object):
    '''Helper class to create PBArray `database`.

    Parameters
    ----------
    directory : str
        Location to save the database.
    '''
    def __init__(self, directory):
        self.directory = directory
        self.data = []
        self.meta = pbarray_pb2.Meta()
        self.head = pbarray_pb2.Head()

        self.head_path = os.path.join(self.directory, 'HEAD')
        self.meta_path = os.path.join(self.directory, 'META')
        self.data_path = os.path.join(self.directory, 'DATA')

    def Write(self):
        '''Write the `database` to disk.
        '''
        with open(self.head_path, 'wb') as f:
            f.write(self.head.SerializeToString())

        with open(self.meta_path, 'wb') as f:
            f.write(self.meta.SerializeToString())

        with open(self.data_path, 'wb') as f:
            for data in self.data:
                f.write(data.SerializeToString())

    def Put(self, data, meta=None):
        '''Add items to the `database`.

        Parameters
        ----------
        data : DataItem
            DataItem from `pbarray_pb2`.
        meta : MetaItem
            MetaItem from `pbarray_pb2`.
        '''
        if meta==None:
            meta = pbarray_pb2.MetaItem()
        meta_list = [meta]
        self.meta.items.extend(meta_list)
        self.data.append(data)
        offset = data.ByteSize()
        self.head.items.append(offset)

class PBArray(object):
    '''Helper class to get data from PBArray `database`.

    Parameters
    ----------
    directory : str
        Location to save the database.
    '''
    def __init__(self, directory):
        self.directory = directory
        self.data = []
        self.meta = pbarray_pb2.Meta()

        self.head_path = os.path.join(self.directory, 'HEAD')
        self.meta_path = os.path.join(self.directory, 'META')
        self.data_path = os.path.join(self.directory, 'DATA')

        with open(self.head_path, 'rb') as f:
            self.head = pbarray_pb2.Head.FromString(f.read())

        self.sizes = numpy.array(self.head.items)
        sizes = [0]
        sizes.extend(list(self.head.items))
        self.offsets = numpy.cumsum(sizes)[0:-1]

        with open(self.meta_path, 'rb') as f:
            self.meta = pbarray_pb2.Meta.FromString(f.read())

        self.data_file = open(self.data_path, 'rb')

        self.num_items = len(self.sizes)

    def Get(self, id):
        '''Get items from the `database`.

        Returns
        -------
        data : DataItem
            DataItem from `pbarray_pb2`.
        meta : MetaItem
            MetaItem from `pbarray_pb2`.
        '''
        self.data_file.seek(self.offsets[id])
        string = self.data_file.read(self.sizes[id])
        data = pbarray_pb2.DataItem.FromString(string)
        meta = self.meta.items[id]
        return (data, meta)
