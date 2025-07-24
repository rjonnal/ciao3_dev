import panel as pn
import random
from ciao3_dev.components import simulator
from ciao3_dev.components import sensors,loops
from ciao3_dev.components import sensors,loops
import sys,os
from matplotlib import pyplot as plt
import numpy as np


css = '''
.bk.panel-widget-box {
font-size: 10px;
}
.bk-input-group {
font-size: 10px;
}
.bk-input {
font-size: 10px;
}
.bk-btn {
font-size: 10px;
}

'''

pn.extension(raw_css=[css])

pn.extension(raw_css=[css])

#pn.extension('vega')
#pn.extension('ipywidgets')

# Set up sensor
#cam = simulator.Simulator()
cam = cameras.PylonCamera()

sensor = sensors.Sensor(cam)
sensor.remove_tip_tilt = True
sensor.sense()

error_buffer = [0]*100

# Set up sensor figure
sensor_figure = plt.figure(figsize=(4,3))
[[ax1,ax2],[ax3,ax4]] = sensor_figure.subplots(2,2)
ax1.set_title('spots')
ax1.set_xticks([])
ax1.set_yticks([])

ax2.set_title('wavefront')
ax2.set_xticks([])
ax2.set_yticks([])

ax3.set_title('zernike coefficients ($\mu m$)')
ax3.set_xlabel('index')

ax4.set_title('wavefront error ($\mu m$ RMS)')
ax4.set_xlabel('iteration')

iterations = list(np.arange(-99,1))

h1 = ax1.imshow(sensor.image,clim=(0,4095),cmap='gray')
h2 = ax2.imshow(sensor.wavefront,cmap='jet')
zidx = np.arange(len(sensor.zernikes))
h3 = ax3.plot(zidx,sensor.zernikes,'ks',markersize=2,linestyle='none')
h4 = ax4.plot(iterations,error_buffer,'b-')


# Widgets
exposure_time_input = pn.widgets.IntInput(name='Exposure Time (ms)', value=150)
background_adjustment_input = pn.widgets.IntInput(name='Background Adjustemnt (ADU)', value=0)
run_toggle = pn.widgets.button.Toggle(name='Run', button_type='primary')
download_button = pn.widgets.Button(name='Download data', button_type='primary')
calibrate_button = pn.widgets.Button(name='Record reference', button_type='primary')
mpl_pane = pn.pane.Matplotlib(sensor_figure, dpi=150)

def increment(x):
    return x + 1

# Callback
count = 0

def on_download(event):
    pass

download_button.on_click(on_download)

def emit_count():
    if not run_toggle.value:
        return
    
    global count,sensor,error_buffer,h1,h2,h3,h4,sensor_figure,mpl_pane
    global ax1,ax2,ax3,ax4,iterations


    
    sensor.cam.set_exposure(1000*exposure_time_input.value)
    sensor.background_correction = background_adjustment_input.value
    sensor.sense()

    iterations = iterations[1:]
    iterations.append(iterations[-1]+1)
    
    error_buffer = error_buffer[1:]
    error_buffer.append(sensor.error*1e6)

    h1.set_data(sensor.image-background_adjustment_input.value)
    h2.set_data(sensor.wavefront)

    zernikes = sensor.zernikes*1e6
    h3[0].set_ydata(zernikes)
    ax3.set_ylim((np.min(zernikes),np.max(zernikes)))

    h4[0].set_xdata(iterations)
    h4[0].set_ydata(error_buffer)
    ax4.set_ylim((np.min(error_buffer),np.max(error_buffer)))
    ax4.set_xlim((iterations[0],iterations[-1]))
    
    #sensor_figure.canvas.draw()
    #sensor_figure.canvas.flush_events()
    mpl_pane.object = sensor_figure
    count += 1

pn.state.add_periodic_callback(emit_count, period=100, count=999);


# Layout

app = pn.Row(pn.Column(pn.pane.Markdown("**CIAO Wavefront Sensor**"),
                       exposure_time_input,
                       background_adjustment_input,
                       run_toggle,
                       download_button,
                       calibrate_button,
                       width=300,
                       css_classes=['panel-widget-box']),
             pn.Column(mpl_pane,
                       width=900),
             )
#servable
app.servable()
