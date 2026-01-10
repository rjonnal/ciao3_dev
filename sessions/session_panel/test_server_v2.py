import panel as pn
import random
from ciao3_dev.components import sensors,loops
import ciao_config as ccfg

if ccfg.camera_id=='pylon':
    from ciao3_dev.components import cameras
elif ccfg.camera_id=='simulator':
    from ciao3_dev.components import simulator
    
import sys,os
from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl

STRIPCHART_BUFFER_LENGTH = 20

pn.extension('terminal')

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
pn.extension(throttled=True, notifications=True)

#pn.extension('vega')
#pn.extension('ipywidgets')

# Set up sensor
if ccfg.camera_id=='pylon':
    cam = cameras.PylonCamera()
elif ccfg.camera_id=='simulator':
    cam = simulator.Simulator()
else:
    sys.exit('%s is not a valid value for camera_id in ciao_config.py'%ccfg.camera_id)
    
sensor = sensors.Sensor(cam)
sensor.remove_tip_tilt = True
sensor.sense()


view_options=['Spots','Profile','Profile fit','Wavefront','Zernike','Error','Defocus','Astig0','Astig45']
figure_dict = {}
axes_dict = {}
for vo in view_options:
    fig = plt.figure(figsize=ccfg.figsize)
    fig.suptitle(vo)
    figure_dict[vo] = fig
    if vo in ['Profile fit','Wavefront']:
        axes_dict[vo] = figure_dict[vo].subplots(subplot_kw={"projection": "3d"})
    else:
        axes_dict[vo] = figure_dict[vo].subplots(1,1)


class View:

    def __init__(self,sensor,fig):
        self.fig = fig
        self.sensor = sensor
        self.ax = fig.axes[0]
        
    def update(self):
        # ...
        pass

class ErrorView(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.buffer_length = STRIPCHART_BUFFER_LENGTH
        self.t = list(range(self.buffer_length))
        self.y = [0]*self.buffer_length
        self.handle = self.ax.plot(self.t,self.y)[0]
        
    def update(self):
        self.y = self.y[1:]+[sensor.error]
        self.handle.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()

class DefocusView(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.buffer_length = STRIPCHART_BUFFER_LENGTH
        self.t = list(range(self.buffer_length))
        self.y = [0]*self.buffer_length
        self.handle = self.ax.plot(self.t,self.y)[0]
        
    def update(self):
        self.y = self.y[1:]+[sensor.zernikes[4]]
        self.handle.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()


class Astig0View(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.buffer_length = STRIPCHART_BUFFER_LENGTH
        self.t = list(range(self.buffer_length))
        self.y = [0]*self.buffer_length
        self.handle = self.ax.plot(self.t,self.y)[0]
        
    def update(self):
        self.y = self.y[1:]+[sensor.zernikes[3]]
        self.handle.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()


class Astig45View(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.buffer_length = STRIPCHART_BUFFER_LENGTH
        self.t = list(range(self.buffer_length))
        self.y = [0]*self.buffer_length
        self.handle = self.ax.plot(self.t,self.y)[0]
        
    def update(self):
        self.y = self.y[1:]+[sensor.zernikes[5]]
        self.handle.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()

        
class ZernikeView(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.idx = np.arange(ccfg.n_zernike_display)
        
    def update(self):
        self.ax.clear()
        bc = self.ax.bar(self.idx,sensor.zernikes[:len(self.idx)]*1e6)
        bc[3].set_facecolor('tab:red')
        bc[4].set_facecolor('tab:green')
        bc[5].set_facecolor('tab:red')
        
class SpotsView(View):

    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.handle = self.ax.imshow(sensor.image)

    def update(self):
        self.handle.set_data(sensor.image)

class ProfileView(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.handle = self.ax.imshow(self.sensor.get_profile()['profile'])
        
    def update(self):
        self.handle.set_data(self.sensor.get_profile()['profile'])

class ProfileFitView(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.handle = self.ax.imshow(self.sensor.get_profile()['gaussian_fit'],cmap='autumn')

    def update(self):
        self.handle.set_data(self.sensor.get_profile()['gaussian_fit'])

class ProfileFitView3D(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        
    def update(self):
        gf = self.sensor.get_profile()['gaussian_fit']
        gf[np.where(gf==0)] = np.nan
        self.ax.clear()
        self.handle = self.ax.plot_surface(self.sensor.mask_XX_m,
                                           self.sensor.mask_YY_m,
                                           gf,cmap='autumn')

class WavefrontView(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        self.handle = self.ax.imshow(self.sensor.get_profile()['wavefront'],cmap='bone')
        
    def update(self):
        self.handle.set_data(self.sensor.get_profile()['wavefront'])

class WavefrontView3D(View):
    def __init__(self,sensor,fig):
        super().__init__(sensor,fig)
        
    def update(self):
        wf = self.sensor.wavefront
        wf[np.where(wf==0)] = np.nan
        self.ax.clear()
        self.handle = self.ax.plot_surface(self.sensor.mask_XX_m,
                                           self.sensor.mask_YY_m,
                                           wf,cmap='bone')
        self.fig.canvas.draw()
        

zv = ZernikeView(sensor,figure_dict['Zernike'])
sv = SpotsView(sensor,figure_dict['Spots'])
pv = ProfileView(sensor,figure_dict['Profile'])
pfv = ProfileFitView3D(sensor,figure_dict['Profile fit'])
wfv = WavefrontView3D(sensor,figure_dict['Wavefront'])
ev = ErrorView(sensor,figure_dict['Error'])
dv = DefocusView(sensor,figure_dict['Defocus'])
a0v = Astig0View(sensor,figure_dict['Astig0'])
a45v = Astig45View(sensor,figure_dict['Astig45'])



im_min = 0
im_max = 2**ccfg.bit_depth-1

# Widgets
exposure_time_input = pn.widgets.IntSlider(name='Exposure Time (us)', start=ccfg.min_exposure_us,end=ccfg.max_exposure_us,step=ccfg.step_exposure_us,value=ccfg.default_exposure_us)

background_adjustment_input = pn.widgets.IntSlider(name='Background Adjustment',start=im_min,end=im_max,step=1,value=0)
#clim_lower_input = pn.widgets.IntSlider(name='Lower Contrast Limt',start=im_min,end=im_max,step=1,value=im_min)
#clim_upper_input = pn.widgets.IntSlider(name='Upper Contrast Limt',start=im_min,end=im_max,step=1,value=im_max)


run_toggle = pn.widgets.RadioButtonGroup(name='Run', button_type='default', options=['Pause', 'Run'], value='Pause'
        )
download_button = pn.widgets.Button(name='Download data', button_type='primary')
calibrate_button = pn.widgets.Button(name='Record reference', button_type='primary')
mode_selector = pn.widgets.Select(name='Select', options=['Spots','Profile','Profile fit','Wavefront','Zernike','Error','Defocus','Astig0','Astig45'])

terminal = pn.widgets.Terminal(
    "Spots image statistics\n",
    options={"cursorBlink": True}, width=280,
    height=200
)

mpl_pane = pn.pane.Matplotlib(figure_dict['Spots'], dpi=150)

# Callback
count = 0

def on_download(event):
    pass

download_button.on_click(on_download)

def emit():
    if not run_toggle.value=='Run':
        return
    
    global count,sensor,mpl_pane,iterations,zv,sv,pv,fpv,wfv,ev,dv,a0v,a45v

    sensor.cam.set_exposure(exposure_time_input.value)
    sensor.background_correction = background_adjustment_input.value
    sensor.sense()

    ev.update()
    dv.update()
    a0v.update()
    a45v.update()
    
    #terminal.write('%d (min) %d (mean) %d (max)\n'%(immin,immean,immax))
    
    if mode_selector.value=='Spots':
        sv.update()
        mpl_pane.object = sv.fig
    elif mode_selector.value=='Zernike':
        zv.update()
        mpl_pane.object = zv.fig
    elif mode_selector.value=='Profile':
        pv.update()
        mpl_pane.object = pv.fig
    elif mode_selector.value=='Profile fit':
        pfv.update()
        mpl_pane.object = pfv.fig
    elif mode_selector.value=='Wavefront':
        wfv.update()
        mpl_pane.object = wfv.fig
    elif mode_selector.value=='Error':
        mpl_pane.object = ev.fig
    elif mode_selector.value=='Defocus':
        mpl_pane.object = dv.fig
    elif mode_selector.value=='Astig0':
        mpl_pane.object = a0v.fig
    elif mode_selector.value=='Astig45':
        mpl_pane.object = a45v.fig
        
    #sensor_figure.canvas.draw()
    #sensor_figure.canvas.flush_events()
    #mpl_pane.object = sensor_figure
    count += 1

pn.state.add_periodic_callback(emit, period=500, count=999);


# Layout

app = pn.Row(pn.Column(pn.pane.Markdown("**CIAO Wavefront Sensor**"),
                       exposure_time_input,
                       background_adjustment_input,
#                       clim_lower_input,
#                       clim_upper_input,
                       run_toggle,
                       download_button,
                       calibrate_button,
                       mode_selector,
                       width=300,
                       css_classes=['panel-widget-box']),
             pn.Column(width=10),
             pn.Column(mpl_pane,
                       width=900),
             )
#servable
app.servable()
