from ciao3_dev.components import simulator
from ciao3_dev.components import sensors,loops
from ciao3_dev.components import sensors,loops
import sys,os
from matplotlib import pyplot as plt

cam = simulator.Simulator()
mirror = cam
sensor = sensors.Sensor(cam)
loop = loops.Loop(sensor,mirror)

for k in range(50):
    loop.update()
    plt.cla()
    plt.imshow(sensor.image)
    plt.xlim((140,150))
    plt.ylim((140,150))
    plt.pause(.0001)
loop.close()
for k in range(50):
    loop.update()
    plt.cla()
    plt.imshow(sensor.image)
    plt.xlim((140,150))
    plt.ylim((140,150))
    plt.pause(.0001)

sys.exit()
