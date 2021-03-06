# -*- coding: utf-8 -*-
# -*- python -*-
#
#       Copyright 2016 INRIA
#
#       File author(s):
#           Sophie Ribes <sophie.ribes@inria.fr>
#           Jerome Chopard <jerome.chopard@inria.fr>
#
#       See accompanying file LICENSE.txt
# -----------------------------------------------------------------------------

"""
This class allows a management of ``SpatialImage`` objects (2D and 3D images).
A ``SpatialImage`` gathers a numpy array and some metadata (such as voxelsize,
physical extent, origin, type, etc.). Through a ``numpy.ndarray`` inheritance, all
usual operations on `numpy.ndarray <http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.ndarray.html>`_
objects (sum, product, transposition, etc.) are available. All image processing
operations are performed on this data structure, that is also used to solve inputs (read)
and outputs (write).
"""

# ----
# SR : update - 08/2016
# numpy types, tests and conds, 2D and 3D management
# origin, voxelsize, extent, mean, min, max and metadata
# set and get methods
# to_2D(), to_3D() methods
# documentation and unit tests (see test_spatial_image.py)

from __future__ import division
import numpy as np
__all__ = ['SpatialImage']
EPS, DEC_VAL = 1e-9, 6


poss_types_dict = { 0: np.uint8, 1: np.int8, 2: np.uint16, 3: np.int16, 4: np.uint32,
                    5: np.int32, 6: np.uint64, 7: np.int64, 8: np.float32, 9: np.float64,
                    10: np.float_, 11: np.complex64, 12: np.complex128, 13: np.complex_,
                    'uint8': np.uint8, 'uint16': np.uint16, 'ushort': np.uint16, 'uint32': np.uint32,
                    'uint64': np.uint64, 'uint': np.uint64, 'ulonglong': np.uint64, 'int8': np.int8,
                    'int16': np.int16, 'short': np.int16, 'int32':np.int32, 'int64':np.int64,
                    'int': np.int64, 'longlong': np.int64, 'float16': np.float16, 'float32': np.float32,
                    'single': np.float32, 'float64': np.float64, 'double': np.float64, 'float': np.float64,
                    'float128': np.float_, 'longdouble': np.float_, 'longfloat': np.float_,
                    'complex64': np.complex64, 'singlecomplex': np.complex64, 'complex128': np.complex128,
                    'cdouble': np.complex128, 'cfloat': np.complex128, 'complex': np.complex128,
                    'complex256': np.complex_, 'clongdouble': np.complex_, 'clongfloat': np.complex_,
                    'longcomplex': np.complex_ }


def around_list(input_list, dec_val=DEC_VAL):
    if isinstance(input_list, list) and len(input_list)>0:
        output_list = [np.around(input_list[ind], decimals=dec_val).tolist()
                       for ind, val in enumerate(input_list)]
        return output_list
    else:
        return []


def tuple_to_list(input_tuple):
    if isinstance(input_tuple, tuple):
        output_list = [input_tuple[ind] for ind, val in enumerate(input_tuple)]
        output_list = around_list(output_list)
        return output_list
    else:
        return []


class SpatialImage(np.ndarray):
    """
    """
    def __new__(cls, input_array, origin=None, voxelsize=None,
                 dtype=None, metadata_dict=None):
        """
        ``SpatialImage`` constructor (2D and 3D images)

        Parameters
        ----------
        :param *numpy.ndarray* input_array: image

        :param list origin: image origin, optional. Default: [0,0] or [0,0,0]

        :param list voxelsize: image voxelsize, optional. Default: [1.0,1.0] or [1.0,1.0,1.0]

        :param str dtype: image type, optional. Default: dtype=input_array.dtype

        :param dict metadata_dict: image metadata, optional. Default: metadata_dict={}

        Returns
        ----------
        :return: ``SpatialImage`` instance -- image and metadata

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image_1 = SpatialImage(input_array=test_array)
        >>> image_2 = SpatialImage(input_array=test_array, voxelsize=[0.5,0.5])
        >>> isinstance(image_1, SpatialImage) and isinstance(image_2, SpatialImage)
        True
        """

        if isinstance(input_array, np.ndarray) and len(input_array.shape) in [2,3]:

            def_type = poss_types_dict[0]
            def_vox_2D, def_vox_3D = [1.0, 1.0], [1.0, 1.0, 1.0]
            def_orig_2D, def_orig_3D = [0, 0], [0, 0, 0]

            if dtype is None or dtype==[]:
                if (input_array.dtype is not None):
                    dtype = input_array.dtype
            elif dtype is not None:
                if (str(dtype) in poss_types_dict.keys() or dtype in poss_types_dict.values()):
                    for key in poss_types_dict:
                        if (str(dtype)==key or dtype==poss_types_dict[key]):
                            dtype = poss_types_dict[key]
                else:
                    print('Available types :'), poss_types_dict
                    print('Setting type to unsigned integer')
                    dtype = def_type

            if input_array.flags.f_contiguous:
                obj = np.asarray(input_array, dtype=dtype).view(cls)
            else :
                obj = np.asarray(input_array, dtype=dtype, order='F').view(cls)

            if origin is None or origin==[]:
                orig = [0 for ind in xrange(len(input_array.shape))]
            elif origin is not None and isinstance(origin, list):
                if len(origin)==(len(input_array.shape)):
                    orig = origin
                else:
                    print('Warning, incorrect specification')
                    if len(input_array.shape)==2:
                        orig = def_orig_2D
                    elif len(input_array.shape)==3:
                        orig = def_orig_3D
                    print('Setting origin to :'), orig

            obj.origin = orig

            if isinstance(voxelsize, tuple):    # SR --- BACK COMPAT
                voxelsize = tuple_to_list(voxelsize)

            if voxelsize is None or voxelsize==[]:
                print('Warning, voxelsize is not defined')
                if (len(input_array.shape)==2):
                    obj.voxelsize = def_vox_2D
                elif (len(input_array.shape)==3):
                    obj.voxelsize = def_vox_3D
                print('Setting voxelsize to : '), obj.voxelsize
            elif voxelsize is not None and len(voxelsize)>0:
                if (len(input_array.shape)!=len(voxelsize)):
                    print('Warning, incorrect specification')
                    if (len(input_array.shape)==2):
                        obj.voxelsize = def_vox_2D
                    elif (len(input_array.shape)==3):
                        obj.voxelsize = def_vox_3D
                    print('Setting voxelsize to : '), obj.voxelsize
                elif (len(input_array.shape)==len(voxelsize)):
                    vox = around_list(voxelsize)
                    obj.voxelsize = vox

            ext = [obj.voxelsize[ind]*input_array.shape[ind] for ind in xrange(len(input_array.shape))]
            ext = around_list(ext)
            obj.extent = ext

            if metadata_dict is None or metadata_dict==[]:
                metadata_dict = {}

            if isinstance(metadata_dict, dict):
                metadata_dict['voxelsize'] = obj.voxelsize
                metadata_dict['shape'] = obj.shape
                metadata_dict['dim'] = obj.ndim
                metadata_dict['origin'] = obj.origin
                metadata_dict['extent'] = obj.extent
                metadata_dict['type'] = str(obj.dtype)
                metadata_dict['min'] = obj.min()
                metadata_dict['max'] = obj.max()
                metadata_dict['mean'] = obj.mean()

            obj.metadata = metadata_dict
            return obj


    def __array_finalize__(self, obj):

        if obj is not None:
            self.voxelsize = getattr(obj, 'voxelsize', [])
            self.origin =  getattr(obj, 'origin', [])
            self.extent = getattr(obj, 'extent', [])
            self.min = getattr(obj, 'min', [])
            self.max = getattr(obj, 'max', [])
            self.mean = getattr(obj, 'mean', [])
            self.metadata = getattr(obj, 'metadata', {})
        else:
            return


#    def __str__(self):
#        return "SpatialImage instance, metadata: {}".format(self.get_metadata())


    def equal(self, sp_img):
        """
        Equality test between two ``SpatialImage``

        Parameters
        ----------
        :param ``SpatialImage`` sp_img: ``SpatialImage`` instance

        Returns
        ----------
        :returns: True/False (*bool*) -- if (array and metadata) are equal/or not

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image_1 = SpatialImage(input_array=test_array)
        >>> image_1==image_1
        True
        >>> image_2 = SpatialImage(input_array=test_array, voxelsize=[0.5,0.5])
        >>> image_1==image_2
        False
        """
        val = False
        if isinstance(sp_img, SpatialImage):
            if self.get_shape() == sp_img.get_shape():
                out_img = np.zeros_like(self, dtype=np.float)
                out_img = np.abs(self - sp_img)
                if np.max(out_img<EPS):
                    conds_arr = True
                conds_met = [True if self.get_metadata()[key]==sp_img.get_metadata()[key]
                             else False for key in self.get_metadata()]
                if conds_arr and (False not in conds_met):
                    val = True
        return val


    def get_array(self):
        """
        Get a ``numpy.ndarray`` from a ``SpatialImage``

        Returns
        ----------
        :returns: image_array (*numpy.ndarray*) -- ``SpatialImage`` array

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_array = image.get_array()
        >>> isinstance(image_array, SpatialImage)
        False
        >>> isinstance(image_array, np.ndarray)
        True
        """
        return np.array(self)


    def get_dim(self):
        """
        Get ``SpatialImage`` dimension (2D or 3D image)

        Returns
        ----------
        :returns: image_dim (*int*) -- ``SpatialImage`` dimension

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_dim = image.get_dim()
        >>> print image_dim
        2
        """
        return self.ndim


    def get_extent(self):
        """
        Get ``SpatialImage`` physical extent

        Returns
        ----------
        :returns: image_extent (*list*) -- ``SpatialImage`` physical extent

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_extent = image.get_extent()
        >>> print image_extent
        [5.0, 5.0]
        """
        return self.extent


    def get_metadata(self):
        """
        Get ``SpatialImage`` metadata

        Returns
        ----------
        :returns: image_metadata (*dict*) -- ``SpatialImage`` metadata

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_metadata = image.get_metadata()
        >>> print image_metadata
        {'dim': 2,
         'extent': [5.0, 5.0],
         'origin': [0, 0],
         'shape': (5, 5),
         'type': 'uint8',
         'voxelsize': [1.0, 1.0]
         }
        """
        met_dict = self.metadata
        if met_dict['shape'] != self.shape:
            old_shape = met_dict['shape']
            met_dict['shape'], met_dict['dim'], met_dict['type'] = self.shape, self.ndim, str(self.dtype)
            if (self.ndim==2 and old_shape[0]==self.shape[1] and old_shape[1]==self.shape[0]): #--- transposition
                vox = [met_dict['voxelsize'][1], met_dict['voxelsize'][0]]
                ext = [met_dict['extent'][1], met_dict['extent'][0]]
                orig = [met_dict['origin'][1], met_dict['origin'][0]]
                met_dict['voxelsize'], met_dict['extent'], met_dict['origin'] = vox, ext, orig
                self.voxelsize, self.extent, self.origin = vox, ext, orig
            elif (self.ndim==3 and old_shape[0] in self.shape and old_shape[1] in self.shape and old_shape[2] in self.shape):
                print('Warning : possibly incorrect voxelsize, extent and origin')
                vox, ext, orig = [], [], []
                for ind in range(0,self.ndim):
                    tmp = old_shape.index(self.shape[ind])
                    vox.append(met_dict['voxelsize'][tmp])
                    ext.append(met_dict['extent'][tmp])
                    orig.append(met_dict['origin'][tmp])
                met_dict['voxelsize'], met_dict['extent'], met_dict['origin'] = vox, ext, orig
                self.voxelsize, self.extent, self.origin = vox, ext, orig
            else:
                print('Warning : incorrect voxelsize, extent and origin')
                vox, ext, orig = [], [], []
                met_dict['voxelsize'], met_dict['extent'], met_dict['origin'] = vox, ext, orig
                self.voxelsize, self.extent, self.origin = vox, ext, orig
        self.metadata = met_dict
        return self.metadata


    def get_min(self):
        """
        Get ``SpatialImage`` min

        Returns
        ----------
        :returns: image_min (*val*) -- ``SpatialImage`` min

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_min = image.get_min()
        >>> print image_min
        1
        """
        return self.min()


    def get_max(self):
        """
        Get ``SpatialImage`` max

        Returns
        ----------
        :returns: image_max (*val*) -- ``SpatialImage`` max

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_max = image.get_max()
        >>> print image_max
        1
        """
        return self.max()


    def get_mean(self):
        """
        Get ``SpatialImage`` mean

        Returns
        ----------
        :returns: image_mean (*val*) -- ``SpatialImage`` mean

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_mean = image.get_mean()
        >>> print image_mean
        1
        """
        return self.mean()


    def get_origin(self):
        """
        Get ``SpatialImage`` origin

        Returns
        ----------
        :returns: image_origin (*list*) -- ``SpatialImage`` origin

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_origin = image.get_origin()
        >>> print image_origin
        [0, 0]
        """
        return self.origin


    def get_pixel(self, indices):
        """
        Get ``SpatialImage`` pixel value

        Parameters
        ----------
        :param list indices: indices as list of integers

        Returns
        ----------
        :returns: pixel_value (*self.get_type()*) -- pixel value

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> indices = [1,1]
        >>> pixel_value = image.get_pixel(indices)
        >>> print pixel_value
        1
        """
        img_dim = self.get_dim()
        if isinstance(indices, list) and len(indices)==img_dim:
            img_shape = self.get_shape()
            if img_dim==2:
                range_x, range_y = xrange(img_shape[0]), xrange(img_shape[1])
                conds_ind = indices[0] in range_x and indices[1] in range_y
            elif img_dim==3:
                range_x, range_y, range_z = xrange(img_shape[0]), xrange(img_shape[1]), xrange(img_shape[2])
                conds_ind = indices[0] in range_x and indices[1] in range_y and indices[2] in range_z
            if conds_ind:
                if img_dim==2:
                    pix_val = self[indices[0],indices[1]]
                elif img_dim==3:
                    pix_val = self[indices[0],indices[1],indices[2]]
            return pix_val
        else:
            print('Warning, incorrect specification')
            return


    def get_region(self, indices):
        """
        Extract a region

        Parameters
        ----------
        :param list indices: indices as list of integers

        Returns
        ----------
        :returns: out_sp_image (``SpatialImage``) -- output ``SpatialImage``

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> indices = [1,3,1,3]
        >>> out_sp_image = image.get_region(indices)
        >>> isinstance(out_sp_image, SpatialImage)
        True
        """
        img_dim = self.get_dim()
        conds = isinstance(indices, list) and len(indices)==2*img_dim
        reg_val = 0
        tmp_arr, tmp_vox = self.get_array(), self.get_voxelsize()
        if conds:
            img_shape = self.get_shape()
            if img_dim==2:
                range_x, range_y = range(0,img_shape[0]+1), range(0, img_shape[1]+1)
                conds_ind = (indices[0] in range_x and indices[1] in range_x
                            and indices[2] in range_y and indices[3] in range_y)
                conds_val = ((max(indices[0],indices[1])>=min(indices[0],indices[1])+1)
                            and (max(indices[2],indices[3])>=min(indices[2],indices[3])+1))
            elif img_dim==3:
                range_x, range_y, range_z = range(0,img_shape[0]+1), range(0, img_shape[1]+1), range(0, img_shape[2]+1)
                conds_ind = (indices[0] in range_x and indices[1] in range_x
                            and indices[2] in range_y and indices[3] in range_y
                            and indices[4] in range_z and indices[5] in range_z)
                conds_val = ((max(indices[0],indices[1])>=min(indices[0],indices[1])+1)
                            and (max(indices[2],indices[3])>=min(indices[2],indices[3])+1)
                            and (max(indices[4],indices[5])>=min(indices[4],indices[5])+1))
            if conds_ind and conds_val:
                if img_dim==2:
                    reg_val = tmp_arr[min(indices[0],indices[1]):max(indices[0],indices[1]),
                                      min(indices[2],indices[3]):max(indices[2],indices[3])]
                elif img_dim==3:

                    reg_val = tmp_arr[min(indices[0],indices[1]):max(indices[0],indices[1]),
                                      min(indices[2],indices[3]):max(indices[2],indices[3]),
                                      min(indices[4],indices[5]):max(indices[4],indices[5])]

                    if 1 in reg_val.shape: # 3D --> 2D
                        if reg_val.shape[0]==1:
                            reg_val = np.squeeze(reg_val, axis=(0,))
                            tmp_vox = [tmp_vox[1],tmp_vox[2]]
                        elif reg_val.shape[1]==1:
                            reg_val = np.squeeze(reg_val, axis=(1,))
                            tmp_vox = [tmp_vox[0],tmp_vox[2]]
                        elif reg_val.shape[2]==1:
                            reg_val = np.squeeze(reg_val, axis=(2,))
                            tmp_vox = [tmp_vox[0],tmp_vox[1]]
            else:
                print('Warning, incorrect specification')
        else:
            print('Warning, incorrect specification')
        out_sp_img = SpatialImage(input_array=reg_val, voxelsize=tmp_vox)
        return out_sp_img


    def get_shape(self):
        """
        Get ``SpatialImage`` shape

        Returns
        ----------
        :returns: image_shape (*tuple*) -- ``SpatialImage`` shape

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_shape = image.get_shape()
        >>> print image_shape
        (5, 5)
        """
        return self.shape


    def get_type(self):
        """
        Get ``SpatialImage`` type

        Returns
        ----------
        :returns: image_type (*str*) -- ``SpatialImage`` type

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_type = image.get_type()
        >>> print image_type
        uint8
        """
        return str(self.dtype)


    def get_voxelsize(self):
        """
        Get ``SpatialImage`` voxelsize

        Returns
        ----------
        :returns: image_voxelsize (*list*) -- ``SpatialImage`` voxelsize

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_voxelsize = image.get_voxelsize()
        >>> print image_voxelsize
        [1.0, 1.0]
        """
        return self.voxelsize


    def set_extent(self, img_extent):
        """
        Set ``SpatialImage`` physical extent

        Parameters
        ----------
        :param list image_extent: ``SpatialImage`` physical extent.
                                Metadata are updated according to the new physical extent.

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_extent = [10.0, 10.0]
        >>> image.set_extent(image_extent)
        """
        if isinstance(img_extent, list) and len(img_extent)==self.get_dim():
            img_extent = around_list(img_extent)
            self.extent = img_extent
            vox = [img_extent[ind]/self.get_shape()[ind] for ind, val in enumerate(img_extent)]
            vox = around_list(vox)
            self.set_voxelsize(vox)
            meta_dict = self.get_metadata()
            meta_dict['extent'] = img_extent
            meta_dict['voxelsize'] = vox
            self.metadata = meta_dict


    def set_metadata(self, img_metadata):
        """
        Set ``SpatialImage`` metadata

        Parameters
        ----------
        :param dict image_metadata: ``SpatialImage`` metadata

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_metadata = {'name':'img_test'}
        >>> image.set_metadata(image_metadata)
        """
        tmp_dict = self.get_metadata()
        if isinstance(img_metadata, dict) and isinstance(tmp_dict, dict):
            tmp_dict.update(img_metadata)
            self.metadata = tmp_dict
            self.origin = tmp_dict['origin']
            self.voxelsize = around_list(tmp_dict['voxelsize'])
            self.extent = around_list(tmp_dict['extent'])
            self.min = tmp_dict['min']
            self.max = tmp_dict['max']
            self.mean = tmp_dict['mean']


    def set_origin(self, img_origin):
        """
        Set ``SpatialImage`` origin

        Parameters
        ----------
        :param list image_origin: ``SpatialImage`` origin

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_origin = [2, 2]
        >>> image.set_origin(image_origin)
        """
        if isinstance(img_origin, list) and len(img_origin)==self.get_dim():
            self.origin = img_origin
            img_met = self.get_metadata()
            img_met['origin'] = self.origin
            self.metadata = img_met


    def set_pixel(self, indices, val):
        """
        Set ``SpatialImage`` pixel value

        Parameters
        ----------
        :param list indices: indices as list of integers

        :param value: new value, type of ``SpatialImage`` array

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> indices = [1,1]
        >>> value = 2
        >>> image.set_pixel(indices, value)
        """
        img_dim = self.get_dim()
        if isinstance(indices, list) and len(indices)==img_dim:
            img_shape = self.get_shape()
            if img_dim==2:
                range_x, range_y = xrange(img_shape[0]), xrange(img_shape[1])
                conds_ind = indices[0] in range_x and indices[1] in range_y
            elif img_dim==3:
                range_x, range_y, range_z = xrange(img_shape[0]), xrange(img_shape[1]), xrange(img_shape[2])
                conds_ind = indices[0] in range_x and indices[1] in range_y and indices[2] in range_z
            if conds_ind:
                if img_dim==2:
                    self[indices[0],indices[1]]=val
                elif img_dim==3:
                    self[indices[0],indices[1],indices[2]]=val
            return
        else:
            print('Warning, incorrect specification')
            return


    def set_region(self, indices, val):
        """
        Replace a region

        Parameters
        ----------
        :param list indices: indices as list of integers
        :param val: new values (*np.ndarray* or value)

        Returns
        ----------
        :returns: out_sp_image (``SpatialImage``) -- ``SpatialImage`` instance

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> indices = [1,3,1,3]
        >>> out_sp_image = image.set_region(indices, 3)
        """
        img_dim = self.get_dim()
        conds_type = isinstance(indices, list) and len(indices)==2*img_dim
        if conds_type:
            conds_type_2 = isinstance(val, np.ndarray)
            conds_type_3 = isinstance(val, int)
            tmp_arr, tmp_vox = self.get_array(), self.get_voxelsize()
            if conds_type_2:
                if img_dim==2:
                    conds_shape = (((max(indices[0],indices[1])-min(indices[0],indices[1]))==val.shape[0])
                                    and ((max(indices[2],indices[3])-min(indices[2],indices[3]))==val.shape[1]))
                elif img_dim==3:
                    conds_shape = (((max(indices[0],indices[1])-min(indices[0],indices[1]))==val.shape[0])
                                    and ((max(indices[2],indices[3])-min(indices[2],indices[3]))==val.shape[1])
                                    and ((max(indices[4],indices[5])-min(indices[4],indices[4]))==val.shape[2]))
                if conds_shape:
                    if img_dim==2:
                        tmp_arr[min(indices[0],indices[1]):max(indices[0],indices[1]),
                                min(indices[2],indices[3]):max(indices[2],indices[3])] = val[:,:]
                    elif img_dim==3:
                        tmp_arr[min(indices[0],indices[1]):max(indices[0],indices[1]),
                                min(indices[2],indices[3]):max(indices[2],indices[3]),
                                min(indices[4],indices[5]):max(indices[4],indices[5])] = val[:,:,:]
            elif conds_type_3:
                if img_dim==2:
                    tmp_arr[min(indices[0],indices[1]):max(indices[0],indices[1]),
                            min(indices[2],indices[3]):max(indices[2],indices[3])] = val
                elif img_dim==3:
                    tmp_arr[min(indices[0],indices[1]):max(indices[0],indices[1]),
                            min(indices[2],indices[3]):max(indices[2],indices[3]),
                            min(indices[4],indices[5]):max(indices[4],indices[5])] = val
        else:
            print('Warning, incorrect specification')
        out_sp_img = SpatialImage(input_array=tmp_arr, voxelsize=tmp_vox)
        return out_sp_img


    def set_type(self, val):
        """
        Set ``SpatialImage`` type

        Parameters
        ----------
        :param str image_type: image type (see numpy types).

        Returns
        ----------
        :returns: out_sp_image (``SpatialImage``) -- ``SpatialImage`` instance

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_type = np.uint16
        >>> out_sp_image = image.set_type(image_type)
        """
        if (val in poss_types_dict.keys() or val in poss_types_dict.values()):
            for key in poss_types_dict:
                if (val==key or val==poss_types_dict[key]):
                    new_type = poss_types_dict[key]

            met_dict = self.get_metadata()
            self = self.astype(new_type)
            met_dict['type'] = str(self.dtype)
            self.metadata = met_dict
            return self


    def set_voxelsize(self, val):
        """
        Set ``SpatialImage`` voxelsize

        Parameters
        ----------
        :param list image_voxelsize: ``SpatialImage`` voxelsize

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array)
        >>> image_voxelsize = [0.5, 0.5]
        >>> image.set_voxelsize(image_voxelsize)
        """
        if isinstance(val, list) and len(val)==self.get_dim():
            val = around_list(val)
            self.voxelsize = val
            ext = [val[ind]*self.shape[ind] for ind, v in enumerate(self.shape)]
            ext = around_list(ext)
            self.extent = ext
            img_met = self.get_metadata()
            img_met['voxelsize'] = self.voxelsize
            img_met['extent'] = self.extent
            self.metadata = img_met


    def to_2D(self):
        """
        3D to 2D
        """
        if (self.get_dim()==3) and (1 in self.get_shape()):
            voxelsize, shape, array = self.get_voxelsize(), self.get_shape(), self.get_array()
            if shape[0]==1:
                new_arr = np.squeeze(array, axis=(0,))
                new_vox = [voxelsize[1], voxelsize[2]]
            elif shape[1]==1:
                new_arr = np.squeeze(array, axis=(1,))
                new_vox = [voxelsize[0], voxelsize[2]]
            elif shape[2]==1:
                new_arr = np.squeeze(array, axis=(2,))
                new_vox = [voxelsize[0], voxelsize[1]]
            out_sp_img = SpatialImage(input_array=new_arr, voxelsize=new_vox)
            return out_sp_img
        else:
            print('sp_img can not be reshaped')
            return


    def to_3D(self):
        """
        2D to 3D
        """
        if (self.get_dim()==2):
            voxelsize, shape, array = self.get_voxelsize(), self.get_shape(), self.get_array()
            new_arr = np.reshape(array, (shape[0], shape[1], 1))
            new_vox = [voxelsize[0], voxelsize[1], 1.0]
            out_sp_img = SpatialImage(input_array=new_arr, voxelsize=new_vox)
            return out_sp_img
        else:
            print('sp_img is not a 2D SpatialImage')
            return


    def revert_axis(self, axis='z'):
        """
        Revert x, y, or z axis

        Parameters
        ----------
        :param str axis: can be either 'x', 'y' or 'z'

        Returns
        ----------
        :returns: out_sp_image (``SpatialImage``) -- ``SpatialImage`` instance

        Example
        -------
        >>> import numpy as np
        >>> from timagetk.components import SpatialImage
        >>> test_array = np.ones((5,5,5), dtype=np.uint8)
        >>> image = SpatialImage(input_array=test_array, voxelsize=[0.5, 0.5, 0.5])
        >>> image.revert_axis(axis='y')
        """
        if self.get_dim()==2:
            self = self.to_3D()

        arr, vox = self.get_array(), self.get_voxelsize()
        if axis=='x':
            new_arr = arr[::-1,:,:]
        if axis=='y':
            new_arr = arr[:,::-1,:]
        elif axis=='z':
            new_arr = arr[:,:,::-1]
        out_sp_image = SpatialImage(new_arr, voxelsize=vox)
        if 1 in out_sp_image.get_shape():
            out_sp_image = out_sp_image.to_2D()
        return out_sp_image