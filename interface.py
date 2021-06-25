##
# Project:  Animations using Fourier Series
# Author: Oscar Mejia

# Aims: The project has an interface that allows the user imports an image, edit colors of background,foreground and arrows_color.
#         The project generate a gif to show the animation and export it automatically
# Based on: https://www.youtube.com/watch?v=r6sGWTCMz2k&t=1337s and additonal information

# Ackwoledgements: Mariana Moreno and Angel Hurtado
##

# Libraries
# Interface
import tkinter
from tkinter import ttk
from tkinter import *
from tkinter import messagebox as MessageBox
from tkinter import scrolledtext as st
from tkinter import filedialog as fd
import tkinter.font as font
from tkinter import colorchooser

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# Image
from PIL import Image, ImageTk
import PIL

from skimage import io
import imageio

import os
import glob


# Librerias
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.fftpack import fft, fftfreq, ifft
import cmath
import ipywidgets as widgets
import imageio as io
import glob
import moviepy.editor as mpy
from IPython.display import IFrame
from IPython.core.display import display

# Global variables used in the code
bg_color = []
arrows_color = []
border_colors = []
orden = 300
fps = 10
duration = 20
filename = ''

# Functions


def Gifgeneration(filename, bc, fc, arrows, orden, fps, duration):
    # Gifgeneration:
    # Steps:
    #     The function imports the selected image in the interface by the user.
    #     Filter it and define edges.
    #     Convert the edges to dot maps
    #     Organize the points to define a closed curve
    #     Apply Fourier Series to define the curve as function of the time
    #     Generate the Gif

    # Parameters:
    #   filename: str. Image's name to be used
    #   bc = list. Color to use in the background
    #   fc = list. Colors of the  foreground or borders in the animation
    #   arrows = list. Color of the arrows.
    #   orden = int. Number of frequencies used on Fourier series (Number of arrows)
    #   fps = int. Frames per second of the gif
    #   duration = int. Duration in seconds of the gif

    #
    m = orden

    # Import file
    import cv2
    original = cv2.imread(filename, 1)
    row, col, d = original.shape

    # Filter
    gris = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gaussiana = cv2.GaussianBlur(gris, (5, 5), 0)

    # Treshold
    _, tresh = cv2.threshold(
        gaussiana, 254, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Generation of dot map
    eje_x = []
    eje_y = []

    for j in range(1, col-1):
        for i in range(1, row-1):
            if tresh[i, j] > 250 and (tresh[i, j-1] != tresh[i, j+1] or tresh[i-1, j] != tresh[i+1, j]):
                eje_x.append(j)
                eje_y.append(i)

    eje_x[:] = (eje_x[:] - np.mean(eje_x))
    eje_y[:] = (eje_y[:] - np.mean(eje_y))*-1

    # ordering and defining the closed curve
    intermedio = pd.DataFrame([], columns=['X', 'Y'])
    intermedio['X'] = eje_x
    intermedio['Y'] = eje_y
    intermedio = intermedio.sort_values(
        by=['X', 'Y'], ignore_index=True, ascending=[True, False])

    Neje_x = [intermedio['X'][0]]
    Neje_y = [intermedio['Y'][0]]

    lista_repetidos = []

    for i in range(0, len(eje_x)-1):

        dis = 1000
        for j in range(1, len(eje_x)):

            d = np.sqrt((Neje_x[i]-intermedio['X'][j]) **
                        2 + (Neje_y[i]-intermedio['Y'][j])**2)

            if d < dis and (j in lista_repetidos) is False and d/len(eje_x) < 0.05:
                dis = d
                indice = j

        lista_repetidos.append(indice)
        Neje_x.append(intermedio['X'][indice])
        Neje_y.append(intermedio['Y'][indice])

    Neje_x.append(intermedio['X'][0])
    Neje_y.append(intermedio['Y'][0])

    # Applying Fourier Series
    # Complex numbers
    eje_x = Neje_x
    eje_y = Neje_y
    N = len(eje_x)  # Number of epyclicles

    # Defining new Complex system base on dot map
    Fcomplex = []

    for k in range(N):
        com = complex(eje_x[k], eje_y[k])
        Fcomplex.append(com)

    Freal = []
    Fimag = []

    for j in np.arange(-m, m, 1):

        a = 0
        b = 0
        for k in range(N):
            a += Fcomplex[k]*cmath.exp(complex(0, -j*k*2*np.pi/N))

        Freal.append(a.real)
        Fimag.append(a.imag)

    # Computing the curve as function of the time
    time = np.linspace(0, 1, fps*duration)
    N_x = []
    N_y = []

    def f(t):
        x = 0
        y = 0
        V_x = [x]
        V_y = [y]
        for k in range(0, 2*m):
            x += Freal[k]*np.cos((k-m)*t*2*np.pi) - \
                Fimag[k]*np.sin((k-m)*t*2*np.pi)
            y += Fimag[k]*np.cos((k-m)*t*2*np.pi) + \
                Freal[k]*np.sin((k-m)*t*2*np.pi)
            V_x.append(x/N)
            V_y.append(y/N)
        return (x, y, V_x, V_y)

    for t in time:
        x, y, V_x, V_y = f(t)
        N_x.append(x/N)
        N_y.append(y/N)

    # Generation the GIF using the settings

    import random
    for i in range(len(N_x)):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        _, _, V_x, V_y = f(time[i])

        ax.plot(V_x, V_y, '->', alpha=0.25, color=arrows)
        if fc == []:
            fc_color = (random.random(), random.random(), random.random(), 1)
        else:
            a = i % len(fc)
            fc_color = fc[a]

        ax.plot(N_x[0:i], N_y[0:i], color=fc_color)
        ax.axis('off')
        ax.set_xlim([min(N_x)-10, max(N_x)+10])
        ax.set_ylim([min(N_y)-10, max(N_y)+10])

        if bc == []:
            fig.patch.set_facecolor('black')
        else:
            fig.patch.set_facecolor(bc)

        plt.savefig("Frames/t{0:04d}.png".format(i),
                    facecolor=fig.get_facecolor())

    file_list = sorted(glob.glob('./Frames/*.png'))
    imgs = []
    for f in file_list:
        imgs.append(io.imread(f))
    io.mimsave('movie.gif', imgs, duration=1/fps)
    return len(time)


# funciones
def openReadme():
    # openReadme: Read and show the README.txt file that cointains intructions of the interface

    try:
        newWindow = tkinter.Toplevel(root)

        with open('README.txt', 'r') as f:
            texto = f.read()
        newLabel = Label(newWindow, text=texto, font=myFont)
        newLabel.pack()

        newWindow.mainloop()
    except Exception:
        MessageBox.showerror('There is not an README file to be showed')


def newImage():
    # neImage: Import and show the selected image in interface
    global filename
    try:
        pil_image = Image.open(filename)
        newWindow = tkinter.Toplevel(root)
        photo2 = ImageTk.PhotoImage(pil_image)
        newLabel = Label(newWindow, image=photo2)
        newLabel.pack()
        newWindow.mainloop()
    except Exception:
        MessageBox.showerror(message='The file has not been imported')


def openFile():
    # openFile: Displays a menu to select the image that will be used

    global photo
    global filename
    filename = fd.askopenfilename(initialdir="./", title="Seleccione file")
    if filename != '':
        try:
            pil_image = Image.open(filename)
            resized = pil_image.resize((250, 250))
            photo = ImageTk.PhotoImage(resized)
            plotOriginal()

        except Exception:
            MessageBox.showerror(message='The selected file is not an Image')


def plotOriginal():
    # plotOriginal: Shows the image in the interface
    global photo
    T_image.config(image=photo)


def choose_bg():
    # choose_bg: Display a Menu to select the background color
    global bg_color
    bg_color = colorchooser.askcolor(title="Choose color for background")
    L_background.config(bg=bg_color[1])


def choose_arrow():
    # choose_arrows: Display a Menu to select the arrows color
    global arrows_color
    arrows_color = colorchooser.askcolor(title="Choose color for arrows")
    L_arrows.config(bg=arrows_color[1])


def choose_border():
    # choose_border: Display a Menu to select the border color
    global border_colors
    temp = colorchooser.askcolor(title="Choose color for borders")
    stgg = ''
    color_temp = temp[1]
    border_colors .append(color_temp)
    E_foreground.insert(END, color_temp+'\n')


def AdvancedConfiguration():
    # AdvancedConfiguration: Displays a menu to redefine: orden, fps and duration

    global orden, fps, duration

    def save_advanced():
        global orden, fps, duration
        orden = int(T_order.get("1.0", 'end-1c'))
        fps = int(T_fps.get("1.0", 'end-1c'))
        duration = int(T_duration.get("1.0", 'end-1c'))

    def reset():
        global orden, fps, duration
        orden = 300
        fps = 10
        duration = 20
        T_order.delete("1.0", END)
        T_fps.delete("1.0", END)
        T_duration.delete("1.0", END)
        T_order.insert(END, str(orden))
        T_fps.insert(END, str(fps))
        T_duration.insert(END, str(duration))

    newWindow = tkinter.Toplevel(root)

    L_order = Label(newWindow, text='Orden', font=myFont, width=15, height=1)
    L_order.grid(row=0, column=0)

    T_order = Text(newWindow, font=myFont, width=15, height=1)
    T_order.grid(row=0, column=1)
    T_order.insert(END, str(orden))

    L_fps = Label(newWindow, text='FPS', font=myFont, width=15, height=1)
    L_fps.grid(row=1, column=0)

    T_fps = Text(newWindow, font=myFont, width=15, height=1)
    T_fps.grid(row=1, column=1)
    T_fps.insert(END, str(fps))

    L_duration = Label(newWindow, text='Duration [sec]',
                       font=myFont, width=15, height=1)
    L_duration.grid(row=2, column=0)

    T_duration = Text(newWindow, font=myFont, width=15, height=1)
    T_duration.grid(row=2, column=1)
    T_duration.insert(END, str(duration))

    B_reset = Button(newWindow, command=reset,
                     font=myFont, width=15, height=1, text='Reset')
    B_reset.grid(row=3, column=1)

    B_save = Button(newWindow, command=save_advanced,
                    font=myFont, width=15, height=1, text='Save')
    B_save.grid(row=3, column=2)

    newWindow.mainloop()


def compute():
    # compute: Save the settings and generates the gif

    global orden, fps, duration
    global filename
    global photo
    global bg_color

    if filename == '':
        MessageBox.showerror(message='The file has not been imported')
        return

    answer = MessageBox.askyesno("Are you sure about that?",
                                 'Do you want to continue using the selected file and settings? \n The process may take time, please do not close the window', default="yes")
    if answer:
        # background
        if bg_color != []:
            bc = list(bg_color[0])
            for i in range(len(bc)):
                bc[i] = bc[i]/255
        else:
            bc = [0, 0, 0]

        global border_colors

        fc = []

        if border_colors != []:
            fc = border_colors

        # Create a empty folder called: Frames
        if os.path.exists('./Frames'):
            py_files = glob.glob('Frames/*.png')
            for py_file in py_files:
                try:
                    os.remove(py_file)
                except OSError as e:
                    print(f"Error:{ e.strerror}")
        else:
            os.mkdir('Frames')

        global arrows_color
        if arrows_color != []:
            arrows = list(arrows_color[0])
            for i in range(len(arrows)):
                arrows[i] = arrows[i]/255
        else:
            arrows = [1, 1, 1]

        frameCnt = Gifgeneration(
            filename, bc, fc, arrows, orden, fps, duration)

        Gif_plot(frameCnt)
        MessageBox.showinfo(message='The process has been donde')

    else:
        MessageBox.showinfo(
            message='Please check the file and settings to continue')


def Gif_plot(frameCnt):
    # Gifplot: Shows the GIF in the interface
    try:
        frames = [PhotoImage(file='movie.gif', format='gif -index %i' % (i))
                  for i in range(frameCnt)]

        def update(ind):

            frame = frames[ind]
            ind += 1
            if ind == frameCnt:
                ind = 0
            T_gif.configure(image=frame)
            root.after(100, update, ind)

        root.after(0, update, 0)

    except Exception:
        MessageBox.ERROR('There is not a GIF to show')


# Interface
root = tkinter.Tk()
root.title('GIF animation')

# Fonts
title = font.Font(family='Courier New Baltic', size=14, weight='bold')
myFont = font.Font(family='Leelawadee UI Semilight', size=14)

# Frames
F_sup = LabelFrame(root)
F_sup.pack(side='top')

F_bot = LabelFrame(root)
F_bot.pack(side='bottom')


# Frame: Top
# File
Lf_file = LabelFrame(F_sup, text='File', font=title)
Lf_file.pack(side='left')

# Buttons of Settings
readme = Button(Lf_file, text='Read me',
                command=openReadme, font=myFont, width=15)

readme.grid(row=0, column=0)
importar = Button(Lf_file, text='Import',
                  command=openFile, font=myFont, width=15)

importar.grid(row=1, column=0)
graficar = Button(Lf_file, text='Plot',
                  command=compute, font=myFont, width=15)

graficar.grid(row=2, column=0)

T_autor = Label(Lf_file, text='Project by Oscar Mejia', font=myFont)
T_autor.grid(row=3, column=0)


# Visualization
Lf_graficos = LabelFrame(
    F_sup, text="Final animation", font=title)
Lf_graficos.pack(fill="both", expand="yes", side='right')

T_gif = Label(Lf_graficos)
T_gif.pack()

# Bottom
# Settings of the GIF
options = LabelFrame(F_bot, text="Configuration",
                     width=500, height=550, font=title)
options.pack(fill="both", expand="yes", side='left')

Imag_base = LabelFrame(F_bot, text="Original Image",
                       width=500, height=600, font=title)
Imag_base.pack(fill="both", expand="yes", side='right')


# Background
B_background = Button(options, command=choose_bg,
                      text='Background', font=myFont, width=20)
B_background.grid(row=1, column=0)
L_background = Label(options, width=20, bg='black')
L_background.grid(row=1, column=1)

# Foreground
L_foreground = Button(options, command=choose_border,
                      text='Colors of borders', font=myFont, width=20)
L_foreground.grid(row=2, column=0)

E_foreground = Text(options, width=20, height=1, font=myFont)
E_foreground.grid(row=2, column=1)

# Arrows
B_arrows = Button(options, command=choose_arrow,
                  text='Color of arrows', font=myFont, width=20)
B_arrows.grid(row=3, column=0)

L_arrows = Label(options, bg='#ffffff', width=20)
L_arrows.grid(row=3, column=1)

T_image = Button(Imag_base, command=newImage)
T_image.pack(fill="both", expand="yes", side='left')

B_advconfiguration = Button(options, command=AdvancedConfiguration,
                            text='Advanced Configuration', font=myFont, width=20)
B_advconfiguration.grid(row=4, column=0)

# Tkinter loop
tkinter.mainloop()
