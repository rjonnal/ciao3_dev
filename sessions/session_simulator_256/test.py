from ciao3_dev.components import simulator
cam = simulator.Simulator()
from ciao3_dev.components import sensors,loops
from ciao3_dev.components import sensors,loops
sensor = sensors.Sensor(cam)
loop = loops.Loop(sensor,cam)
sensor.sense()
loop.update()

