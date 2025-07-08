import numpy as np
import time
from ciao3_dev.components import centroid
import sys
import os
from matplotlib import pyplot as plt
import datetime
import cProfile
from ctypes import CDLL,c_void_p
from ciao3_dev.components.search_boxes import SearchBoxes
import ciao_config as ccfg
import json
from ciao3_dev.components.simulator import Simulator
from ciao3_dev.components import cameras
from ciao3_dev.components.mirrors import Mirror
from ciao3_dev.components.ui import UI
from ciao3_dev.components.frame_timer import FrameTimer
from ciao3_dev.components.zernike import Reconstructor
from ciao3_dev.components.tools import error_message, now_string, prepend, colortable, get_ram, get_process
from ciao3_dev.components.sensors import Sensor

        
if __name__=='__main__':
    if ccfg.simulate:
        sim = Simulator()
        sensor = Sensor(sim)
        mirror = sim
    else:
        cam = cameras.get_camera()
        mirror = Mirror()
        sensor = Sensor(cam)

sensor.pseudocalibrate()

