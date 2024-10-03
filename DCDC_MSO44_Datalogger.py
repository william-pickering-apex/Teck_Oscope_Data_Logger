
from tm_devices import DeviceManager
from tm_devices.drivers import MSO6B, MSO4B
from tm_devices.helpers import PYVISA_PY_BACKEND

import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from tm_devices import DeviceManager


"""An example showing a basic curve query."""
def curveQuery():
    from tm_devices import DeviceManager

    EXAMPLE_CSV_FILE = "example_curve_query.csv"

    with DeviceManager(verbose=True) as dm:
        scope = dm.add_scope("169.254.10.140")
        #afg = dm.add_afg("169.254.10.140")

        # Turn on AFG
        scope.set_and_check(":OUTPUT1:STATE", "1")
        scope.poll_query()

        # Perform curve query and save results to csv file
        curve_returned = scope.curve_query(1, output_csv_file=EXAMPLE_CSV_FILE)

    # Read in the curve query from file
    with open(EXAMPLE_CSV_FILE, encoding="utf-8") as csv_content:
        curve_saved = [int(i) for i in csv_content.read().split(",")]

    # Verify query saved to csv is the same as the one returned from curve_query function call
    assert curve_saved == curve_returned

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
        #scope.set_and_check("DATA:SOURCE", f"CH{1}")

        #wfm_str = scope.query(":CURVE?")
        #frames = wfm_str.splitlines()[0].split(";")
        for frame in scope.curve_query(1):
            #tempval=[int(b) for b in frame.split(",")]
            #print(frame)
            self.data[:-1] = self.data[1:]  # Shift data to the left
            self.data[-1] = frame  # Add new random data
            self.curve.setData(self.data)  # Update the plot

    def run(self):
        # Start the application

        self.app.exec_()
with DeviceManager(verbose=False) as device_manager:
    global scope
    # Enable resetting the devices when connecting and closing
    device_manager.setup_cleanup_enabled = True
    device_manager.teardown_cleanup_enabled = False

    # Use the PyVISA-py backend
    device_manager.visa_library = PYVISA_PY_BACKEND

    # Creating Scope driver object by providing ip address.
    scope: MSO4B = device_manager.add_scope("169.254.10.140")

    # Turn on channel 1 and channel 2
    scope.commands.display.waveview1.ch[1].state.write("ON")
    scope.commands.display.waveview1.ch[2].state.write("ON")
    scope.commands.display.waveview1.ch[3].state.write("ON")
    scope.commands.display.waveview1.ch[4].state.write("ON")

    # Set channel 1 vertical scale to 10mV
    scope.commands.ch[1].scale.write(5)
    scope.commands.ch[2].scale.write(5)
    scope.commands.ch[3].scale.write(5)
    scope.commands.ch[4].scale.write(5)
    scope.commands.horizontal.scale.write(2000)

    # Set horizontal record length to 20000
    #scope.commands.horizontal.scale.write(0.0004)

    # Set horizontal position to 100
    scope.commands.horizontal.position.write(10)
    # EXAMPLE_CSV_FILE = "C:/Users/WilliamPickering/PycharmProjects/Teck_Oscope_Data_Logger/example_curve_query.csv"
    # Perform curve query and save results to csv file
    # scope.curve_query(1, output_csv_file=EXAMPLE_CSV_FILE)

    # Read in the curve query from file
    # with open(EXAMPLE_CSV_FILE, encoding="utf-8") as csv_content:
    #    curve_saved = [int(i) for i in csv_content.read().split(",")]
    if __name__ == '__main__':
        plotter = LivePlotter()
        plotter.run()

#simpleDataTrigger()
#curveQuery()

#curve_returned_out = dataLogger()
#print(curve_returned_out)