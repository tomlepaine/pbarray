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
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.meta_head = pbarray_pb2.MetaHead()
        self.data_head = pbarray_pb2.DataHead()

        self.meta_head_path = os.path.join(self.directory, 'METAHEAD')
        self.data_head_path = os.path.join(self.directory, 'DATAHEAD')
        self.meta_path = os.path.join(self.directory, 'META')
        self.data_path = os.path.join(self.directory, 'DATA')

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

        meta_offset = meta.ByteSize()
        self.meta_head.items.append(meta_offset)
        
        data_offset = data.ByteSize()
        self.data_head.items.append(data_offset)

        # Write items
        with open(self.meta_path, 'ab') as f:
            f.write(meta.SerializeToString())

        with open(self.data_path, 'ab') as f:
            f.write(data.SerializeToString())
                
    def Close(self):
        # Rewrite heads
        with open(self.meta_head_path, 'wb') as f:
            f.write(self.meta_head.SerializeToString())
            
        with open(self.data_head_path, 'wb') as f:
            f.write(self.data_head.SerializeToString())
            
class PBArray(object):
    '''Helper class to get data from PBArray `database`.
    Parameters
    ----------
    directory : str
        Location to save the database.
    '''
    def __init__(self, directory):
        self.directory = directory

        self.meta_head_path = os.path.join(self.directory, 'METAHEAD')
        self.data_head_path = os.path.join(self.directory, 'DATAHEAD')
        self.meta_path = os.path.join(self.directory, 'META')
        self.data_path = os.path.join(self.directory, 'DATA')

        # Open headers
        with open(self.meta_head_path, 'rb') as f:
            self.meta_head = pbarray_pb2.MetaHead.FromString(f.read())
            
        with open(self.data_head_path, 'rb') as f:
            self.data_head = pbarray_pb2.DataHead.FromString(f.read())

            
        assert len(self.meta_head.items) == len(self.data_head.items)
        self.num_items = len(self.meta_head.items)
            
        self.meta_offsets = numpy.array(self.meta_head.items)
        self.data_offsets = numpy.array(self.data_head.items)
        
        # add zero to beginning and drop end value
        self.meta_cumulative_offsets = numpy.cumsum(numpy.hstack((0, self.meta_offsets)))[0:-1]
        self.data_cumulative_offsets = numpy.cumsum(numpy.hstack((0, self.data_offsets)))[0:-1]

        self.meta_file = open(self.meta_path, 'rb')
        self.data_file = open(self.data_path, 'rb')


    def Get(self, id):
        '''Get items from the `database`.
        Returns
        -------
        data : DataItem
            DataItem from `pbarray_pb2`.
        meta : MetaItem
            MetaItem from `pbarray_pb2`.
        '''
        self.meta_file.seek(self.meta_cumulative_offsets[id])
        meta_string = self.meta_file.read(self.meta_offsets[id])
        meta = pbarray_pb2.MetaItem.FromString(meta_string)
        
        self.data_file.seek(self.data_cumulative_offsets[id])
        data_string = self.data_file.read(self.data_offsets[id])
        data = pbarray_pb2.DataItem.FromString(data_string)

        return (data, meta)