from warnings import catch_warnings

from tm_devices.drivers import MSO6B, MSO4B
from tm_devices.helpers import PYVISA_PY_BACKEND
#import pyvisa
import time
from tm_devices import DeviceManager

from numpy.ma.core import append

def set_falling_edge_trigger(ch, trigger_val):
    #set_falling_edge_trigger(1, 27) will set Trigger to channel 1 falling edge of 27V
    scope.commands.trigger.a.edge.source.write("CH"+str(ch))
    scope.commands.trigger.a.edge.slope.write("FALL")
    scope.commands.trigger.a.level.ch[ch].write(trigger_val)

def set_peak_to_peak_measurement(ch):
    try:
        scope.write("MEASUrement:ADDMeas PK2PK")
        scope.write("MEASUrement:MEAS{}:SOUrce CH{}".format(ch,ch))
    except Exception as e:
        #minor timeout
        print("timed out on pkpk")

file_base_name = input("Enter Test Name: ")
file_base_name=file_base_name.replace(" ","_").replace('"','')
with DeviceManager(verbose=False) as device_manager:
    global scope
    # Enable resetting the devices when connecting and closing
    device_manager.setup_cleanup_enabled = True
    device_manager.teardown_cleanup_enabled = False
    # Use the PyVISA-py backend
    device_manager.visa_library = PYVISA_PY_BACKEND
    try:
        # Creating Scope driver object by providing ip address.
        scope: MSO4B = device_manager.add_scope("169.254.10.140")
    except Exception as e:
        print("Connection Failed, trying again")
        # Creating Scope driver object by providing ip address.
        scope: MSO4B = device_manager.add_scope("169.254.10.140")

    # Turn on channel 1 and channel 2
    scope.commands.display.waveview1.ch[1].state.write("ON")
    scope.commands.ch[1].scale.write(2)
    scope.commands.ch[1].offset.write(28)
    scope.commands.display.waveview1.ch[2].state.write("ON")
    scope.commands.ch[2].scale.write(1)
    scope.commands.display.waveview1.ch[3].state.write("ON")
    scope.commands.ch[3].scale.write(2)
    scope.commands.ch[3].offset.write(28)
    scope.commands.display.waveview1.ch[4].state.write("ON")
    scope.commands.ch[4].scale.write(1)
    scope.commands.horizontal.scale.write(0.002)

    #scope.commands.display.specview1.viewstyle.write("OVErlay")

    set_falling_edge_trigger(1, 27.5)
    set_peak_to_peak_measurement(1)
    #wait for scope to settle
    time.sleep(5)


    scope.write("ISplay:SPECView1:VIEWStyle OVErlay")
    print(scope.query("MEASUrement:MEAS1:RESUlts:CURRentacq:MAXimum?"))

    scope.write('SEARCH:ADDNEW “SEARCH1”')
    time.sleep(1)
    scope.write("SEARCH:SEARCH1:TRIGGER:A:EDGE:SLOPE RISE")
    scope.write("SEARCH:SEARCH1:TRIGGER:A:EDGE:SOURCE CH1")
    scope.write("SEARCH:SEARCH1:TRIGger:A:EDGE:THReshold 29")

    scope.write('SEARCH:ADDNEW “SEARCH2”')
    time.sleep(1)
    scope.write("SEARCH:SEARCH2:TRIGGER:A:EDGE:SLOPE RISE")
    scope.write("SEARCH:SEARCH2:TRIGGER:A:EDGE:SOURCE CH1")
    scope.write("SEARCH:SEARCH2:TRIGger:A:EDGE:THReshold 27")


    scope.write("ACTONEVent:SEARCH:ACTION:SAVEIMAGe:STATE ON")
    scope.write('SAVEONEVENT:FILENAME "{}"'.format(file_base_name))
    #print(scope.query("MEASUrement:MEAS1:RESUlts:ALLAcqs:PK2PK?"))