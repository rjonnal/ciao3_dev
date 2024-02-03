try:
    import playsound
    use_audio = True
except ImportError as ie:
    use_audio = False
    
import ciao_config as ccfg
import sys
import numpy as np
import time
import os
import logging


class Beeper:

    def __init__(self,nskip=3):

        self.interval = nskip+1
        self.n = 0
        self.active = ('audio_directory' in dir(ccfg) and 'error_tones' in dir(ccfg) and use_audio)
        self.tone_dict = {}

    def cache_tones(self):
        if self.active:
            logging.info('Caching beeper tones...')
            for minmax,tone_string in ccfg.error_tones:
                key = self.err_to_int(minmax[0])
                tonefn = os.path.join(ccfg.audio_directory,'%s.wav'%tone_string)
                self.tone_dict[key] = tonefn
            logging.info('Done!')
        else:
            logging.info('Not caching tone filenames because use_audio is False.')
            
    def err_to_int(self,err):
        return int(np.floor(err*1e8))

    def beep(self,error_in_nm):
        if self.active:
            k = self.err_to_int(error_in_nm)
            if k in list(self.tone_dict.keys()) and self.n==0:
                fn = self.tone_dict[k]
                playsound.playsound(fn)
        else:
            pass
        self.n = (self.n+1)%self.interval

