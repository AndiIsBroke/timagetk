# -*- coding: utf-8 -*-
# -*- python -*-
#
#
#       Copyright 2016 INRIA
#
#       File author(s):
#           Guillaume Baty <guillaume.baty@inria.fr>
#           Sophie Ribes <sophie.ribes@inria.fr>
#           Gregoire Malandain <gregoire.malandain@inria.fr>
#
#       See accompanying file LICENSE.txt
#------------------------------------------------------------------------------

#--- Aug. 2016
from ctypes import POINTER
import numpy as np
try:
    from timagetk.wrapping.clib import libblockmatching, add_doc
    from timagetk.wrapping.balImage import BAL_IMAGE
    from timagetk.wrapping.balTrsf import BAL_TRSF
    from timagetk.wrapping.bal_image import BalImage, init_c_bal_image, allocate_c_bal_image, spatial_image_to_bal_image_fields
    from timagetk.wrapping.bal_matrix import init_c_bal_matrix, allocate_c_bal_matrix
    from timagetk.wrapping.bal_trsf import BalTransformation
    from timagetk.components.spatial_image import SpatialImage
    from ctypes import pointer
except ImportError:
    raise ImportError('Import Error')

__all__ = [
            'INV_TRSF_DEFAULT', 'inv_trsf',
            'APPLY_TRSF_DEFAULT', 'apply_trsf',
            'COMPOSE_TRSF_DEFAULT', 'compose_trsf',
            'CREATE_TRSF_DEFAULT', 'create_trsf',
            'mean_trsfs'
            ]

INV_TRSF_DEFAULT = ''
APPLY_TRSF_DEFAULT = ''
COMPOSE_TRSF_DEFAULT = ''
CREATE_TRSF_DEFAULT = '-identity'


def inv_trsf(bal_transformation, template_img=None,
             param_str_1=INV_TRSF_DEFAULT, param_str_2=None):
    """
    Inversion of a *BalTransformation* transformation

    Parameters
    ----------
    :param *BalTransformation* bal_transformation: *BalTransformation*, input transformation

    :param template_img: optional, default is None. template_img is used for output image geometry
                                                    and can be either SpatialImage or a list of dimensions

    :param str param_str_1: INV_TRSF_DEFAULT, default = ''

    :param str param_str_2: optional, optional parameters

    Returns
    ----------
    :return: output *BalTransformation* transformation

    Example
    -------
    >>> trsf_output = inv_trsf(trsf_input)
    """
    if isinstance(bal_transformation, BalTransformation):

        if template_img is not None:
            if isinstance(template_img, SpatialImage):
                if template_img.get_dim()==2:
                    template_img = template_img.to_3D()
                x, y, z = template_img.get_shape()
                vx, vy, vz = template_img.get_voxelsize()
                val_vox = ''.join([' -template-voxel ', str(vx), ' ', str(vy), ' ', str(vz)])
            elif isinstance(template_img, list):
                if len(template_img)==3:
                    x, y, z = template_img[0], template_img[1], template_img[2]
                elif len(template_img)==2:
                    x, y, z = template_img[0], template_img[1], 1
                val_vox = ''
            val_dim = ''.join([' -template-dim ', str(x), ' ', str(y), ' ', str(z)])
            param_str_1 = ''.join([param_str_1, str(val_dim), str(val_vox)])

        trsf_out = BalTransformation(trsf_type=bal_transformation.trsf_type,
                                     trsf_unit=bal_transformation.trsf_unit,
                                     c_bal_trsf=bal_transformation)
        libblockmatching.API_invTrsf(bal_transformation.c_ptr, trsf_out.c_ptr,
                                     param_str_1, param_str_2)
        return trsf_out
    else:
        raise TypeError('Input transformation must be a BalTransformation')
        return


def apply_trsf(image, bal_transformation=None, template_img=None,
               param_str_1=APPLY_TRSF_DEFAULT, param_str_2=None, dtype=None):
    """
    Apply a *BalTransformation* transformation to a *SpatialImage image

    Parameters
    ----------
    :param *SpatialImage* image: input *SpatialImage*

    :param *BalTransformation* bal_transformation: input *BalTransformation* transformation

    :param template_img: optional, default is None. template_img is used for output image geometry
                                                    and can be either SpatialImage or a list of dimensions

    :param str param_str_1: APPLY_TRSF_DEFAULT

    :param str param_str_2: optional, optional parameters

    :param *np.dtype* dtype  optional, output image type. By default, the output type is equal to the input type.

    Returns
    ----------
    :return: *SpatialImage* output image

    Example
    -------
    >>> output_image = apply_trsf(input_image, input_trsf)
    """
    if isinstance(image, SpatialImage):
        if image.get_dim()==2: # 2D management
            image = image.to_3D()

        if template_img is None:
            kwds = spatial_image_to_bal_image_fields(image)
        elif template_img is not None:
            if isinstance(template_img, SpatialImage):
                if template_img.get_dim()==2:
                    template_img = template_img.to_3D()
                x, y, z = template_img.get_shape()
                vx, vy, vz = template_img.get_voxelsize()
                val_vox = ''.join([' -template-voxel ', str(vx), ' ', str(vy), ' ', str(vz)])
            elif isinstance(template_img, list):
                if len(template_img)==3:
                    tmp_img = np.zeros((template_img[0], template_img[1], template_img[2]), dtype=image.dtype)
                elif len(template_img)==2:
                    tmp_img = np.zeros((template_img[0], template_img[1]), dtype=image.dtype)
                template_img = SpatialImage(tmp_img)
                if template_img.get_dim()==2:
                    template_img = template_img.to_3D()
                x, y, z = template_img.get_shape()
                val_vox = ''
            val_dim = ''.join([' -template-dim ', str(x), ' ', str(y), ' ', str(z)])
            param_str_1 = ''.join([param_str_1, str(val_dim), str(val_vox)])
            kwds = spatial_image_to_bal_image_fields(template_img)

        if dtype is not None:
            kwds['np_type'] = dtype

        c_img_res = BAL_IMAGE()
        init_c_bal_image(c_img_res, **kwds)
        allocate_c_bal_image(c_img_res, np.ndarray(kwds['shape'], kwds['np_type']))
        bal_img_res = BalImage(c_bal_image=c_img_res)
        bal_image = BalImage(image)
        libblockmatching.API_applyTrsf(bal_image.c_ptr, bal_img_res.c_ptr,
                                       bal_transformation.c_ptr if bal_transformation else None,
                                       param_str_1, param_str_2)
        res = bal_img_res.to_spatial_image()
        if 1 in res.get_shape():
            res = res.to_2D()
        bal_image.free(), bal_img_res.free()
        return res
    else:
        raise TypeError('Input image must be a SpatialImage and input transformation must be a BalTransformation')
        return


def compose_trsf(list_trsf, template_img=None,
                 param_str_1=COMPOSE_TRSF_DEFAULT, param_str_2=None):
    """
    Composition of *BalTransformation* transformations

    Parameters
    ----------
    :param list list_trsf: list of *BalTransformation* transformations

    :param *SpatialImage* template_img: optional, template_img is a *SpatialImage* specified for vectorfield composition

    :param str param_str_1: COMPOSE_TRSF_DEFAULT

    :param str param_str_2: optional, optional parameters

    Returns
    ----------
    :return: res_trsf, *BalTransformation* transformation

    Examples
    -------
    >>> res_trsf = compose_trsf([trsf_1, trsf_2, trsf_3])
    >>> res_trsf = compose_trsf([trsf_1, trsf_2, trsf_3], template_img=template_img)
    """
    # SR - 18/03
    trsf_types = [list_trsf[ind].trsf_type for ind, val in enumerate(list_trsf)]
    ref = list_trsf[trsf_types.index(max(trsf_types))]
    # if template_img is not None and 12 (vectorfield transformation)
    # not in trsf_types, template_img is ignored
    if 12 in trsf_types and template_img is None:
        print('Specify a template image for output image geometry')
        raise NotImplementedError
    elif 12 in trsf_types and template_img is not None:
        if template_img.get_dim()==2:
            template_img = template_img.to_3D()
        x, y, z = template_img.get_shape()
        str_dims = ''.join(['-template-dim ', str(x), ' ', str(y), ' ', str(z)])
        param_str_1 = ''.join([param_str_1, str_dims])
        trsf_out = BalTransformation(trsf_type=ref.trsf_type,
                                     trsf_unit=ref.trsf_unit,
                                     c_bal_trsf=ref.c_struct)
    else:
        trsf_out = BalTransformation(trsf_type=ref.trsf_type,
                                     trsf_unit=ref.trsf_unit)
    # end modif

    mat_out = trsf_out.mat
    init_c_bal_matrix(mat_out.c_struct, l=4, c=4)
    allocate_c_bal_matrix(mat_out.c_struct, np.zeros((4, 4), dtype=np.float64))
    ntrsf = len(list_trsf)
    lst = POINTER(BAL_TRSF) * ntrsf
    trsfs = lst(*[trsf.c_ptr for trsf in list_trsf])

    libblockmatching.API_composeTrsf(trsfs, ntrsf, trsf_out.c_ptr,
                                     param_str_1, param_str_2)
    return trsf_out


def create_trsf(template_img=None, param_str_1=CREATE_TRSF_DEFAULT, param_str_2=None,
                trsf_type=None, trsf_unit=None):
    """
    Creation of classical *BalTransformation* transformations such as identity,
    translation, rotation,sinusoidal, random, etc.

    Parameters
    ----------
    :param *SpatialImage* template_img: optional, template_img is a *SpatialImage*

    :param str param_str_1: CREATE_TRSF_DEFAULT, default is identity

    :param str param_str_2: optional, optional parameters

    :param *BalTransformationType* trsf_type: type of *BalTransformation* transformation (see enumTypeTransfo in bal_stddef)
                    Default trsf_type is BalTransformation.AFFINE_3D

    :param *BalTransformationUnit* trsf_unit: unit of *BalTransformation* transformation (see enumUnitTransfo in bal_stddef)
            Default trsf_unit is BalTransformation.REAL_UNIT

    Returns
    ----------
    :return: *BalTransformation* trsf_out, output transformation

    Example
    -------
    >>> identity_trsf = create_trsf()
    """
    if template_img is not None and isinstance(template_img, SpatialImage):
        if template_img.get_dim()==2:
            template_img = template_img.to_3D()

        x, y, z = template_img.get_shape()
        vx, vy, vz = template_img.get_voxelsize()
        val_dim = ''.join([' -template-dim ', str(x), ' ', str(y), ' ', str(z)])
        val_vox = ''.join([' -template-voxel ', str(vx), ' ', str(vy), ' ', str(vz)])
        param_str_1 = ''.join([param_str_1, str(val_dim), str(val_vox)])
        bal_image = BalImage(template_img)
    else:
        template_img = None
        #raise NotImplementedError

    if trsf_type is None:
        trsf_type = BalTransformation.AFFINE_3D
    if trsf_unit is None:
        trsf_unit = BalTransformation.REAL_UNIT

    trsf_out = BalTransformation(trsf_type=trsf_type, trsf_unit=trsf_unit)
    mat_out = trsf_out.mat
    init_c_bal_matrix(mat_out.c_struct, l=4, c=4)
    allocate_c_bal_matrix(mat_out.c_struct, np.zeros((4, 4), dtype=np.float64))
    libblockmatching.API_createTrsf(trsf_out.c_ptr, None if template_img is None else bal_image.c_ptr, param_str_1, param_str_2)
    return trsf_out


def mean_trsfs(list_trsf):
    """
    Mean trsfs (vectorfield) *BalTransformation* transformation

    Parameters
    ----------
    :param list list_trsf: list of *BalTransformation* transformations (vectorfield type)

    Returns
    ----------
    :return: *BalTransformation* trsf_out, output mean transformation

    Example
    -------
    >>> trsf_out = mean_trsf([trsf_1, trsf_2, trsf_3])
    """
    conds_init = isinstance(list_trsf, list) and len(list_trsf)>=2
    conds_list_trsf = [0 if (isinstance(trsf, BalTransformation) and trsf.trsf_type==12)
                       else 1 for trsf in list_trsf]
    conds_inst = len(np.unique(conds_list_trsf))==1 and 1 not in conds_list_trsf

    if conds_init and conds_inst: # list of BalTransformation transformations (vectorfield)

        spatial_image_vx = [trsf.vx.to_spatial_image() for trsf in list_trsf]
        sum_spatial_image_vx = np.zeros_like(spatial_image_vx[0])
        for ind, sp_img in enumerate(spatial_image_vx):
            sum_spatial_image_vx = sum_spatial_image_vx + sp_img
        mean_spatial_image_vx = sum_spatial_image_vx/len(spatial_image_vx)
        mean_spatial_image_vx = SpatialImage(mean_spatial_image_vx,
                                             voxelsize=spatial_image_vx[0].voxelsize)
        BalImage_vx = BalImage(mean_spatial_image_vx)

        spatial_image_vy = [trsf.vy.to_spatial_image() for trsf in list_trsf]
        sum_spatial_image_vy = np.zeros_like(spatial_image_vy[0])
        for ind, sp_img in enumerate(spatial_image_vy):
            sum_spatial_image_vy = sum_spatial_image_vy + sp_img
        mean_spatial_image_vy = sum_spatial_image_vy/len(spatial_image_vy)
        mean_spatial_image_vy = SpatialImage(mean_spatial_image_vy,
                                             voxelsize=spatial_image_vy[0].voxelsize)
        BalImage_vy = BalImage(mean_spatial_image_vy)

        spatial_image_vz = [trsf.vz.to_spatial_image() for trsf in list_trsf]
        sum_spatial_image_vz = np.zeros_like(spatial_image_vz[0])
        for ind, sp_img in enumerate(spatial_image_vz):
            sum_spatial_image_vz = sum_spatial_image_vz + sp_img
        mean_spatial_image_vz = sum_spatial_image_vz/len(spatial_image_vz)
        mean_spatial_image_vz = SpatialImage(mean_spatial_image_vz,
                                             voxelsize=spatial_image_vz[0].voxelsize)
        BalImage_vz = BalImage(mean_spatial_image_vz)

        out_BAL_TRSF = BAL_TRSF() #--- BALTRSF instance
        out_BAL_TRSF_ptr = pointer(out_BAL_TRSF)
        libblockmatching.BAL_AllocTransformation(out_BAL_TRSF_ptr, list_trsf[0].trsf_type,
                                                 pointer(list_trsf[0].vx.c_struct))
        out_BAL_TRSF.transformation_unit = list_trsf[0].trsf_unit
        out_BAL_TRSF.mat = list_trsf[0].mat.c_struct #--- BAL_MATRIX instance
        out_BAL_TRSF.vx = BalImage_vx.c_struct #--- BALIMAGE instance
        out_BAL_TRSF.vy = BalImage_vy.c_struct #--- BALIMAGE instance
        out_BAL_TRSF.vz = BalImage_vz.c_struct #--- BALIMAGE instance
        trsf_out = BalTransformation(trsf_type=list_trsf[0].trsf_type,
                                     c_bal_trsf=out_BAL_TRSF)
        for ind, trsf in enumerate(list_trsf):
            trsf.free()
        return trsf_out
    else:
        print('Specify a list of BalTransformation transformations')
        return


add_doc(inv_trsf, libblockmatching.API_Help_invTrsf)
add_doc(apply_trsf, libblockmatching.API_Help_applyTrsf)
add_doc(compose_trsf, libblockmatching.API_Help_composeTrsf)
add_doc(create_trsf, libblockmatching.API_Help_createTrsf)