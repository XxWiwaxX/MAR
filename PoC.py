import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import struct
import pyaudio


import sys
import time


class AudioStream(object):
    def __init__(self):

        # pyqtgraph stuff
        pg.setConfigOptions(antialias=True)
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title="Spectrum Analyzer")
        self.win.setWindowTitle("Spectrum Analyzer")
        self.win.setGeometry(5, 115, 1910, 1070)

        wf_xlabels = [(0, "0"), (2048, "2048"), (4096, "4096")]
        wf_xaxis = pg.AxisItem(orientation="bottom")
        wf_xaxis.setTicks([wf_xlabels])

        wf_yaxis = pg.AxisItem(orientation="left")

        sp_xlabels = [(20, "20"), (440, "440"), (880, "880"), (20000, "20000")]
        sp_xaxis = pg.AxisItem(orientation="bottom")
        sp_xaxis.setTicks([sp_xlabels])

        sp_xlabels2 = [(20, "20"), (440, "440"), (880, "880"), (20000, "20000")]
        sp_xaxis2 = pg.AxisItem(orientation="bottom")
        sp_xaxis2.setTicks([sp_xlabels2])

        self.waveform = self.win.addPlot(title="WAVEFORM", row=1, col=1, axisItems={"bottom": wf_xaxis, "left": wf_yaxis})
        self.spectrum = self.win.addPlot(title="SPECTRUM", row=2, col=1, axisItems={"bottom": sp_xaxis})
        self.negspectrum = self.win.addPlot(title="negSPECTRUM", row=3, col=1, axisItems={"bottom": sp_xaxis2})


        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1024 * 2

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )
        # waveform and spectrum x points
        self.x = np.arange(0, 2 * self.CHUNK, 2)
        self.xfft = np.linspace(0, self.RATE, self.CHUNK, 2)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
            QtGui.QGuiApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == "waveform":
                self.traces[name] = self.waveform.plot(pen="c", width=3)
                self.waveform.setYRange(-4096, 4096, padding=0)
                self.waveform.setXRange(0, 2 * self.CHUNK, padding=0)
            if name == "spectrum":
                self.traces[name] = self.spectrum.plot(pen="m", width=3)
                self.spectrum.setYRange(-3, 3, padding=0)
                self.spectrum.setXRange(20, 20000, padding=0)
            if name == "negspectrum":
                self.traces[name] = self.negspectrum.plot(pen="m", width=3)
                self.negspectrum.setYRange(-3, 3, padding=0)
                self.negspectrum.setXRange(20, 20000, padding=0)               

    def update(self):
        wf_data = self.stream.read(self.CHUNK)
        wf_data = struct.unpack( str( self.CHUNK ) + "h", wf_data )
        self.set_plotdata(name="waveform", data_x=self.x, data_y=wf_data,)
        sp_data = np.fft.fft(np.array(wf_data, dtype="int16"))
        sp_data = np.abs(sp_data) * 2 / (128 * self.CHUNK)
        self.set_plotdata(name="spectrum", data_x=self.xfft, data_y=sp_data)
        self.set_plotdata(name="negspectrum", data_x=self.xfft, data_y=sp_data*-1)        

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


if __name__ == "__main__":
    audio_app = AudioStream()
    audio_app.animation()