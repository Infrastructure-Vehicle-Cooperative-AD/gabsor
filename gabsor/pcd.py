# -*- coding: utf-8 -*-
"""
Example:

# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z intensity ring time
SIZE 4 4 4 4 2 4
TYPE F F F F U F
COUNT 1 1 1 1 1 1
WIDTH 32886
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS 32886
DATA binary
"""
import os
import laspy
import struct
import numpy as np
from .utils import debug
from typing import Tuple

class PCDReader():
    def __init__(self):
        pass
    
    @staticmethod
    def type_trans(type_list: list) -> Tuple[str , int]:
        ret_type = "<"
        ret_len = 0
        for t in type_list:
            if t == "F":
                ret_type += 'f'
                ret_len += 4
            elif t == "U":
                ret_type += 'H'
                ret_len += 2
            else:
                print('Unknow type', t)
        return ret_type, ret_len
    
    @staticmethod
    def read_pcd(file_path: str) -> dict:
        with open(file_path, 'rb') as file:
            fmt = file.readline().decode()
            version = file.readline().decode()
            fields = file.readline().decode()
            size = file.readline().decode()
            data_type = file.readline().decode()
            conut = file.readline().decode()
            width = file.readline().decode()
            height = file.readline().decode()
            viewpoint = file.readline().decode()
            points = file.readline().decode()
            encode_type = file.readline().decode()

            fields_name = fields.split()[1:]
            s_type, s_len = PCDReader.type_trans(data_type.split()[1:])
            points_num = int(points.split()[1])
            
            data_dict = {field:[] for field in fields_name}
            for i in range(points_num):
                line = file.read(s_len)
                data = struct.unpack(s_type, line)
                for i in range(len(fields_name)):
                    field = fields_name[i]
                    data_dict[field].append(data[i])
        
        for field in fields_name:
            if isinstance(data_dict[field][0], float):
                data_dict[field] = np.asarray(data_dict[field], np.float32)
            elif isinstance(data_dict[field][0], int):
                data_dict[field] = np.asarray(data_dict[field], np.uint16)
            else:
                data_dict[field] = np.asarray(data_dict[field])
        return data_dict
    
    @staticmethod
    def compress_pcd(input_file: str, output_file: str, debug_flag: bool = False) -> None:
        assert input_file.endswith('.pcd'), debug('Error: the input file must be in pcd format', 'error')
        assert output_file.endswith('.laz'), debug('Error: the output file must end with .laz', 'error')
        data_dict = PCDReader.read_pcd(input_file)
        header = laspy.LasHeader(version="1.2", point_format=3)
        for key in data_dict.keys():
            if key in ['x', 'y', 'z', 'intensity']:
                continue
            else:
                if debug_flag: debug('add_extra_dim: '+ key + ', data type: ' + str(data_dict[key].dtype), 'debug')
                header.add_extra_dim(laspy.ExtraBytesParams(name=key, type=data_dict[key].dtype))
                
        header.offsets = np.array([np.min(data_dict['x']), np.min(data_dict['y']), np.min(data_dict['z'])])
        header.scales = np.array([1.0, 1.0, 1.0])
        las = laspy.LasData(header)
        for key in data_dict.keys():
            if debug_flag: debug(key + ': '+ str(data_dict[key].dtype), 'debug')
            setattr(las, key, data_dict[key])
        las.write(output_file)
        
        if debug_flag:
            org_size = os.path.getsize(input_file)
            out_size = os.path.getsize(output_file)
            debug('PointCloud compress rate:'+str(round(100*out_size/org_size, 1))+'%', 'success')
    
    @staticmethod
    def read_compress_pcd(input_file: str) -> dict:
        las = laspy.read(input_file)
        laspy.convert(las)
        data_dict = {'x':np.asarray(las.x, np.float32),
                     'y':np.asarray(las.y, np.float32),
                     'z':np.asarray(las.z, np.float32)}
        if las.intensity.shape[0] > 0:
            data_dict['intensity'] = las.intensity

        for key in list(las.point_format.extra_dimension_names):
            data_dict[key] = getattr(las, key)
        
        return data_dict