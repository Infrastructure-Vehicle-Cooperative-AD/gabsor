# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from .utils import debug

class ImgReader():
    def __init__(self):
        pass
    
    @staticmethod
    def encode_img(img: np.ndarray, isGrey: bool = False) -> bytes:
        if isGrey:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
        ret, jpeg=cv2.imencode('.jpg', img)
        data = jpeg.tobytes()
        return data

    @staticmethod
    def decode_img(data: bytes) -> np.ndarray:
        nparr = np.fromstring(data, np.uint8)
        img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def compress_img(img, output_file: str, debug_flag: bool = False) -> None:
        assert output_file.endswith('.npy'), debug('Error: the output file must end with .npy', 'error')
        # img = cv2.imread(input_file)
        data = ImgReader.encode_img(img)
        np.save(output_file, data)
        
        if debug_flag:
            org_size = os.path.getsize(input_file)
            out_size = os.path.getsize(output_file)
            debug('Image compress rate:'+str(round(100*out_size/org_size, 1))+'%', 'success')
            
    @staticmethod
    def read_compress_img(input_file: str) -> np.ndarray:
        data = np.load(input_file)
        img = ImgReader.decode_img(data)
        return img