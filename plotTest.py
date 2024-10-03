import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore


class LivePlotter:
    def __init__(self):
        # Create the main application and the main window
        self.app = QtWidgets.QApplication(sys.argv)
        self.win = pg.GraphicsLayoutWidget(show=True, title="Live Plotting Example")
        self.win.setWindowTitle('Live Plotting Example')

        # Create a plot item
        self.plot = self.win.addPlot(title="Random Data")
        self.curve = self.plot.plot(pen='y')

        # Initialize data
        self.data = np.zeros(1000)

        # Timer to update the plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # Update every 100 milliseconds

    def update(self):
        # Update data
        self.data[:-1] = self.data[1:]  # Shift data to the left
        self.data[-1] = np.random.normal()  # Add new random data
        self.curve.setData(self.data)  # Update the plot

    def run(self):
        # Start the application
        self.app.exec_()


if __name__ == '__main__':
    plotter = LivePlotter()
    plotter.run()
