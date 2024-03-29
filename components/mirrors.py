import numpy as np
import time
from . import centroid
import sys
import os
from matplotlib import pyplot as plt
import datetime
from ciao3_dev.components.tools import error_message, now_string, prepend, colortable, get_ram, get_process
import copy
from ciao3_dev.components.zernike import Reconstructor
import cProfile
import scipy.io as sio
from ciao3_dev.components.poke_analysis import save_modes_chart
from ctypes import CDLL,c_void_p
from ciao3_dev.components.search_boxes import SearchBoxes
from ciao3_dev.components.reference_generator import ReferenceGenerator
import ciao_config as ccfg
from ciao3_dev.components.frame_timer import FrameTimer
import json

class MirrorController(object):
    def __init__(self):
        self.cmax = ccfg.mirror_command_max
        self.cmin = ccfg.mirror_command_min
        self.command = np.zeros(ccfg.mirror_n_actuators,dtype=np.double)
        self.clipped = False
        
    def clip(self):
        self.clipped = (self.command.max()>=self.cmax or self.command.min()<=self.cmin)
        if self.clipped:
            self.command = np.clip(self.command,self.cmin,self.cmax)
                
    def set(self,vec):
        self.command[:] = vec[:]
        
    def send(self):
        return 1
        
class MirrorControllerCtypes(MirrorController):
    def __init__(self):
        super(MirrorControllerCtypes,self).__init__()
        self.acedev5 = CDLL("acedev5")
        self.mirror_id = self.acedev5.acedev5Init(0)
        self.command = np.zeros(ccfg.mirror_n_actuators,dtype=np.double)
        self.command_ptr = self.command.ctypes.data_as(c_void_p)
        self.send()
        
    def set(self,vec):
        assert len(vec)==len(self.command)
        self.command[:] = vec[:]

    def send(self):
        self.clip()
        return self.acedev5.acedev5Send(self.mirror_id,self.command_ptr)
        
        
class MirrorControllerPython(MirrorController):
    def __init__(self):
        from Lib64.asdk import DM
        super(MirrorControllerPython,self).__init__()        
        self.mirror_id = ccfg.mirror_id
        #self.dm = DM(os.path.join(ccfg.dm_directory,self.mirror_id))
        self.dm = DM(self.mirror_id)
        
        n_actuators_queried = int( self.dm.Get('NBOfActuator') )
        try:
            assert n_actuators_queried==ccfg.mirror_n_actuators
        except AssertionError as ae:
            print('Number of actuator disagreement.')
        self.command[:] = 0.0 # this doesn't really matter
        
    def set(self,vec):
        self.command[:] = vec[:]
        
    def send(self):
        self.clip()
        return self.dm.Send(self.command)
        
        
class MirrorControllerPythonOld(MirrorController):

    def __init__(self):
        super(MirrorControllerPythonOld,self).__init__()
        sys.path.append(os.path.dirname(__file__))
        from .PyAcedev5 import PyAcedev5
        mirrorID = os.path.join(ccfg.dm_directory,ccfg.mirror_id)
        self.dm = PyAcedev5(ccfg.mirror_id)
        n_actuators_queried = int(self.dm.GetNbActuator())
        try:
            assert n_actuators_queried==ccfg.mirror_n_actuators
        except AssertionError as ae:
            print('Number of actuator disagreement.')
        self.command[:] = 0.0 # this doesn't really matter
        
    def set(self,vec):
        self.command[:] = vec[:]
        
    def send(self):
        self.clip()
        self.dm.values[:] = self.command[:]
        return self.dm.Send()

        
        
class Mirror:
    def __init__(self):
        
        self.controller = MirrorControllerPython()
        self.mirror_mask = np.loadtxt(ccfg.mirror_mask_filename)
        self.n_actuators = ccfg.mirror_n_actuators
        self.flat = np.loadtxt(ccfg.mirror_flat_filename)
        self.flat0 = np.loadtxt(ccfg.mirror_flat_filename)
        self.command_max = ccfg.mirror_command_max
        self.command_min = ccfg.mirror_command_min
        self.settling_time = ccfg.mirror_settling_time_s
        self.update_rate = ccfg.mirror_update_rate
        self.flatten()
        self.frame_timer = FrameTimer('Mirror',verbose=False)
        self.logging = False
        self.paused = False
        os.makedirs(ccfg.logging_directory,exist_ok=True)
        
    def update(self):
        if not self.paused:
            self.send()
        if self.logging:
            self.log()
        self.frame_timer.tick()

    def pause(self):
        print('mirror paused')
        self.paused = True

    def unpause(self):
        print('mirror unpaused')
        self.paused = False

    def send(self):
        self.controller.send()

    def flatten(self):
        self.controller.set(self.flat)
        self.send()

    def set_actuator(self,index,value):
        self.controller.command[index] = value
        self.send()
        
    def set_command(self,vec):
        self.controller.set(vec)
        
    def get_command(self):
        return self.controller.command
        
        
    def restore_flat(self):
        self.flat[:] = self.flat0[:]
        
    def set_flat(self):
        self.flat[:] = self.get_command()[:]
        np.savetxt(os.path.join(ccfg.dm_directory,'custom_flat_%s.txt'%now_string()),self.flat)
        
    def log(self):
        now = now_string()
        d = {}
        d['command'] = [float(a) for a in self.controller.command]
        with open(os.path.join(ccfg.logging_directory,'mirror_%s.json'%now),'w') as fid:
            outstr = json.dumps(d)
            fid.write(outstr)
        

    def set_logging(self,val):
        self.logging = val
