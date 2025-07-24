from ciao3_dev.components import simulator
from ciao3_dev.components import sensors,loops
from ciao3_dev.components import sensors,loops
import sys,os
from matplotlib import pyplot as plt

cam = simulator.Simulator()
mirror = cam
sensor = sensors.Sensor(cam)
loop = loops.Loop(sensor,mirror)
loop.run_poke()
