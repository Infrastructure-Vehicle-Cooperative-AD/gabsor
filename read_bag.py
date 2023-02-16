#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gabsor.ros_interface import ROSInterface

bag_path = 'resource/test.bag'
ROSInterface.compress_bag(bag_path)