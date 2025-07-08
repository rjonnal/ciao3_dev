import panel as pn
import random
from ciao3_dev.components import simulator
from ciao3_dev.components import sensors,loops
from ciao3_dev.components import sensors,loops
import sys,os
from matplotlib import pyplot as plt

pn.extension()
from streamz import Stream

#pn.extension('vega')


# Widgets
exposure_time_input = pn.widgets.IntInput(name='Exposure Time (ms)', value=20)
background_adjustment_input = pn.widgets.IntInput(name='Background Adjustemnt (ADU)', value=0)
start_button = pn.widgets.Button(name='Start', button_type='primary')
pause_button = pn.widgets.Button(name='Pause', button_type='primary')
result_display = pn.pane.Markdown("### Result: None")

def increment(x):
    return x + 1

source = Stream()

streamz_pane = pn.pane.Streamz(source.map(increment), always_watch=True)

# Callback
def on_start(event):
    pass

def on_pause(event):
    pass

start_button.on_click(on_start)
pause_button.on_click(on_pause)

count = 1
def emit_count():
    global count
    count += 1
    result_display.object = f"### Result: {count}"
    source.emit(count)

pn.state.add_periodic_callback(emit_count, period=500, count=999);


# Layout
app = pn.Column(pn.pane.Markdown("# CIAO Wavefront Sensor"),
                pn.Row(pn.Column(exposure_time_input,
                                 background_adjustment_input,
                                 start_button,
                                 pause_button,
                                 width=400),
                       pn.Column(result_display,
                                 width=400),
                       width=800))
#servable
app.servable()
