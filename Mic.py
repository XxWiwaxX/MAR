import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import time


# constants
CHUNK = 1024 * 2             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 48000                 # samples per second

# create matplotlib figure and axes
fig, (ax, ax2) = plt.subplots(2)

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# variable for plotting
x = np.arange(0, 2 * CHUNK, 2)
xfft = np.linspace(0, RATE, CHUNK, 2)

# create a line object with random data
line, = ax.plot(x, np.random.rand(CHUNK), "-r", lw=2)
line_fft, = ax2.plot(xfft, np.random.rand(CHUNK), "-r", lw=1)

# basic formatting for the axes
ax.set_title('AUDIO WAVEFORM')
ax.set_xlabel('samples')
ax.set_ylabel('volume')
ax.set_ylim(-2**12, 2**12)
ax.set_xlim(0, 2 * CHUNK)
ax2.set_xlim(20, 5000)
plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[-4096, 0, 4096])
plt.setp(ax2, xticks=[20, 5000, 10000, 15000, 20000], yticks=[0, 4096])

# show the plot

plt.tight_layout()
plt.show(block=False)

while True:
    
    # binary data
    data = stream.read(CHUNK)
  
    # create np array
    data_np = np.frombuffer(data, dtype = np.int16)*5   #times 5 for amplification, needs to be readjusted for absolute Magnitude
    line.set_ydata(data_np)
    line_fft.set_ydata(np.abs(np.fft.fft(data_np)[0:CHUNK])*2/CHUNK)

    #draw line
    fig.canvas.draw()
    fig.canvas.flush_events()
