#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rosbag
from visualization_msgs.msg import *
from sensor_msgs.msg import *
from std_msgs.msg import *
from geometry_msgs.msg import *
from tf2_msgs.msg import *

import os
import numpy as np
from copy import deepcopy as cp

from .pcd import PCDReader
from .img import ImgReader

class ROSInterface():
    def __init__(self):
        pass
    
    @staticmethod
    def get_pcd_fields_name(fields):
        name_list = []
        for field in fields:
            name_list.append(field.name)
        return name_list

    @staticmethod
    def trans_bytes_type(fields):
        """
        INT8 = 1
        UINT8 = 2
        INT16 = 3
        UINT16 = 4
        INT32 = 5
        UINT32 = 6
        FLOAT32 = 7
        FLOAT64 = 8
        """
        ret_type = "<"
        ret_len = 0
        for field in fields:
            if field.datatype == 7:
                ret_type += 'f'
                ret_len += 4
            elif field.datatype == 4:
                ret_type += 'H'
                ret_len += 2
            else:
                print('Unknow type', field)
        return ret_type, ret_len

    @staticmethod
    def read_pcd(msg):
        fields_name = ROSInterface.get_pcd_fields_name(msg.fields)
        data_dict = {field:[] for field in fields_name}
        points_num = msg.width
        s_type, _ = ROSInterface.trans_bytes_type(msg.fields)
        s_len = msg.point_step

        for i in range(points_num):
            line = msg.data[i*s_len : (i+1)*s_len]
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
    def get_msg_attr(msg):
        attr_list = []
        for attr in dir(msg):
            if attr.startswith('_'):
                continue
            if attr in ['deserialize','deserialize_numpy','serialize','serialize_numpy']:
                continue
            attr_list.append(attr)
        
        return attr_list

    @staticmethod
    def get_header_info(header, domain):
        return  {
            domain + '/' + 'frame_id': header.frame_id,
            domain + '/' + 'seq': header.seq,
            domain + '/' + 'stamp': header.stamp.to_nsec(),
        }

    @staticmethod
    def get_pcd_field(msg, domain=''):
        new_domain = cp(domain)
        dict_list = []
        for i in range(len(msg.fields)):
            d = {
                new_domain+'/'+str(i)+'/name': msg.fields[i].name,
                new_domain+'/'+str(i)+'/offset': msg.fields[i].offset,
                new_domain+'/'+str(i)+'/datatype': msg.fields[i].datatype,
                new_domain+'/'+str(i)+'/count': msg.fields[i].count,
            }
            dict_list.append(d)
        
        ret= []
        for d in dict_list:
            ret += d.items()
        return dict(ret)

    @staticmethod
    def get_msg_all(msg, domain='', pass_domain=[]):
        attr_list = ROSInterface.get_msg_attr(msg)
        ret_dict = {}
        for attr in attr_list:
            new_domain = cp(domain)
            new_domain += '/'
            new_domain += attr

            if new_domain in pass_domain:
                continue

            if attr == 'header':
                new_ret_dict = ROSInterface.get_header_info(msg.header, new_domain)
                ret_dict.update(new_ret_dict.items())
                continue

            if type(getattr(msg, attr)).__name__.startswith('_'):
                new_ret_dict = ROSInterface.get_msg_all(getattr(msg, attr), new_domain, pass_domain)
                ret_dict.update(new_ret_dict.items())
            else:
                ret_dict[new_domain] = getattr(msg, attr)
        return ret_dict

    @staticmethod
    def change_topic_name(topic):
        return topic.replace('/', '\\')

    @staticmethod
    def compress_bag(bag_path, save_path=None):
        if save_path is None:
            save_path = bag_path+'.compress/'
        os.makedirs(save_path, exist_ok=True)
        with rosbag.Bag(bag_path, 'r') as bag:
            for topic,msg,t in bag.read_messages():
                msg_type = (msg._type).split('/')[-1]

                if msg_type == 'PointCloud2':
                    data_dict = ROSInterface.read_pcd(msg)

                    ret_dict = ROSInterface.get_msg_all(msg, topic+':', [topic+':/data', topic+':/fields'])
                    new_ret_dict = ROSInterface.get_pcd_field(msg, topic+':/feilds')
                    ret_dict.update(new_ret_dict.items())

                    sub_path = save_path + ROSInterface.change_topic_name(topic) + '/'
                    os.makedirs(sub_path, exist_ok=True)
                    PCDReader.compress_pcd(data_dict, sub_path + str(t)+'.laz')
                    np.save(sub_path + str(t)+'_meta.npy', ret_dict)

                elif msg_type == 'Image':
                    img = np.ndarray(shape=(msg.height, msg.width, 3), dtype=np.dtype("uint8"), buffer=msg.data)
                    ret_dict = ROSInterface.get_msg_all(msg, topic+':', [topic+':/data'])

                    sub_path = save_path + ROSInterface.change_topic_name(topic) + '/'
                    os.makedirs(sub_path, exist_ok=True)
                    ImgReader.compress_img(img, sub_path + str(t)+'.npy')
                    np.save(sub_path + str(t)+'_meta.npy', ret_dict)
                    
                else:
                    ret_dict = ROSInterface.get_msg_all(msg, topic+':')
                    sub_path = save_path + ROSInterface.change_topic_name(topic) + '/'
                    os.makedirs(sub_path, exist_ok=True)
                    np.save(sub_path + str(t)+'.npy', ret_dict)

