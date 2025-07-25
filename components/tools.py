import sys, os
from matplotlib import pyplot as plt
import datetime
import psutil
import numpy as np
import time
import scipy.signal as sps

def get_process():
    return psutil.Process(os.getpid())

def get_ram():
    return (get_process().memory_info().rss)//1024//1024

def error_message(message):
    error_dialog = QErrorMessage()
    error_dialog.setWindowModality(Qt.WindowModal)
    error_dialog.showMessage(message)
    error_dialog.exec_()

def now_string(ms=False):
    if ms:
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")[:-3]
    else:
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")



def prepend(full_path_fn,prefix):
    p,f = os.path.split(full_path_fn)
    return os.path.join(p,'%s_%s'%(prefix,f))

def colortable(colormap_name):
    if colormap_name=='mirror':
        colorcode_saturated = True
        colormap_name = 'gray'
    else:
        colorcode_saturated = False
        
    try:
        cmapobj = plt.get_cmap(colormap_name)
    except AttributeError as ae:
        print('\'%s\' is not a valid colormap name'%colormap_name)
        print('using \'bone\' instead')
        cmapobj = plt.get_cmap('bone')
    ncolors = cmapobj.N

    cmap = np.uint8(cmapobj(list(range(ncolors)))[:,:3]*255.0)
    table = []
    for row in range(cmap.shape[0]):
        table.append(qRgb(cmap[row,0],cmap[row,1],cmap[row,2]))

    if colorcode_saturated:
        table[0] = qRgb(0,0,255)
        table[-1] = qRgb(255,0,0)
        
    return table

def gaussian_convolve(im,sigma,mode='same',hscale=1.0,vscale=1.0):
    if not sigma:
        return im
    else:
        kernel_width = np.ceil(sigma*8) # 4 standard deviations gets pretty close to zero
        vec = np.arange(kernel_width)-kernel_width/2.0
        XX,YY = np.meshgrid(vec,vec)
        g = np.exp(-((XX/hscale)**2+(YY/vscale)**2)/2.0/sigma**2)
        return sps.fftconvolve(im,g,mode=mode)/np.sum(g)
