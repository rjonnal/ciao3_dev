from ciao3_dev.components import simulator
from ciao3_dev.components import sensors
from matplotlib import pyplot as plt
import sys,os

cam = simulator.Simulator()
sensor = sensors.Sensor(cam)

for k in range(100):
    sensor.update()
    plt.cla()
    plt.imshow(sensor.image)
    plt.xlim((120,150))
    plt.ylim((120,150))
    plt.pause(.0001)

sys.exit()
