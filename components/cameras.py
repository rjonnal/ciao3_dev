import numpy as np
import glob
import ciao_config as ccfg
import os,sys
try:
    from pypylon import pylon
except Exception as e:
    print(e)

try:
    from ximea import xiapi
except Exception as e:
    print(e)
    
from ctypes import *
from ctypes.util import find_library
from time import time

def get_camera():
    if ccfg.camera_id.lower()=='pylon':
        return PylonCamera()
    elif ccfg.camera_id.lower()=='ace':
        return AOCameraAce()
    elif ccfg.camera_id.lower()=='ximea':
        return XimeaCamera()
    else:
        sys.exit('Invalid camera type: %s.'%ccfg.camera_id)


class PylonCamera:

    def __init__(self,timeout=500):
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())

        self.camera.Open()
        self.camera.PixelFormat.Value = ccfg.pixel_format
        # enable all chunks
        self.camera.ChunkModeActive = True
        
        for cf in self.camera.ChunkSelector.Symbolics:
            self.camera.ChunkSelector = cf
            self.camera.ChunkEnable = True

        self.timeout = timeout
        self.image = None

        # Enable sensor binning
        # Note: Available on selected camera models only
        self.camera.BinningSelector.Value = "Sensor"
        # Enable horizontal binning by 4
        self.camera.BinningHorizontal.Value = ccfg.binning_horizontal
        # Enable vertical binning by 2
        self.camera.BinningVertical.Value = ccfg.binning_vertical
        # Set the horizontal binning mode to Average
        self.camera.BinningHorizontalMode.Value = "Average"
        # Set the vertical binning mode to Sum
        self.camera.BinningVerticalMode.Value = "Average"

        
    def get_image(self):
        self.image = self.camera.GrabOne(self.timeout).Array.astype(np.int16)
        return self.image
    
    def close(self):
        return

    def set_exposure(self,exposure_us):
        self.camera.ExposureTime.Value = float(exposure_us)
        return
        
    def get_exposure(self):
        return int(self.camera.ExposureTime.Value)

    
    

class XimeaCamera:

    def __init__(self,timeout=500):
        self.camera = xiapi.Camera()
        self.camera.open_device()
        try:
            self.set_exposure(ccfg.camera_exposure_us)
        except AttributeError as ae:
            print(ae)
            print("ciao_config.py is missing an entry for exposure time; please put 'camera_exposure_us = 1000' or similar into the ciao_config.py file for your session")
            sys.exit()
        self.camera.start_acquisition()
        self.img = xiapi.Image()
        self.image = None

    def get_image(self):
        self.camera.get_image(self.img)
        self.image = np.reshape(np.frombuffer(self.img.get_image_data_raw(),dtype=np.uint8),
                          (self.img.height,self.img.width)).astype(np.int16)
        return self.image
    
    def close(self):
        self.camera.stop_acquisition()
        self.camera.close_device()
        
    def set_exposure(self,exposure_us):
        print(exposure_us)
        self.camera.set_exposure(exposure_us)
        
    def get_exposure(self):
        return self.camera.get_exposure()

