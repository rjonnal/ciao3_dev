from ciao3_dev.components import sensors,loops
import ciao_config as ccfg
from ciao3_dev.components import simulator
import sys,os
from matplotlib import pyplot as plt
import numpy as np

cam = simulator.Simulator()
#plt.imshow(cam.get_image())
#plt.colorbar()
#plt.show()

sensor = sensors.Sensor(cam)
sensor.remove_tip_tilt = True
sensor.sense()

prof = sensor.get_profile()
plt.imshow(prof['profile'])
plt.colorbar()
plt.show()

