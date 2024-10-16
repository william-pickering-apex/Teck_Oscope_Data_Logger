from warnings import catch_warnings

from tm_devices.drivers import MSO6B, MSO4B
from tm_devices.helpers import PYVISA_PY_BACKEND
#import pyvisa
import time
from tm_devices import DeviceManager

from numpy.ma.core import append

with DeviceManager(verbose=False) as device_manager:
    global scope
    device_manager.visa_library = PYVISA_PY_BACKEND
    try:
        # Creating Scope driver object by providing ip address.
        scope: MSO4B = device_manager.add_scope("169.254.10.140")
    except Exception as e:
        print("Connection Failed, trying again")
        # Creating Scope driver object by providing ip address.
        scope: MSO4B = device_manager.add_scope("169.254.10.140")
        scope.commands.ch[2].scale.write(1)
        scope.commands.ch[2].offset.write(34)
        scope.commands.ch[4].scale.write(.1)
        scope.commands.ch[4].offset.write(0.5)