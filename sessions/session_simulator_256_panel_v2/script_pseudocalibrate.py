import panel as pn
import random
from ciao3_dev.components import simulator
from ciao3_dev.components import sensors,loops
import sys,os
from matplotlib import pyplot as plt
import numpy as np

        
if __name__=='__main__':
    cam = simulator.Simulator()
    sensor = sensors.Sensor(cam)

    sensor.pseudocalibrate()

