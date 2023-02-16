#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from gabsor.pcd import PCDReader
from gabsor.img import ImgReader

debug_flag = True
PCDReader.compress_pcd('resources/test.pcd', 'resources/test.laz', debug_flag)
data_dict = PCDReader.read_compress_pcd('resources/test.laz')

ImgReader.compress_img('resources/test.png', 'resources/test.npy', debug_flag)
img = ImgReader.read_compress_img('resources/test.npy')

org_size = 15*60*(728*10+990*4*20)/1024/1024
cmp_size = 15*60*(141*10+228*4*20)/1024/1024
print(org_size, cmp_size)