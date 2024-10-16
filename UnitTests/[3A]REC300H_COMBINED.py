from warnings import catch_warnings

from tm_devices.drivers import MSO6B, MSO4B
from tm_devices.helpers import PYVISA_PY_BACKEND
#import pyvisa
import time
from tm_devices import DeviceManager
import pyvisa
import BKP_9141
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
target_output=12
minimum_allowable=11.5
maximum_allowable=12.75
target_current = 0.25
min_input_cur=0.3
max_input_cur=0.2

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
    scope.commands.display.waveview1.ch[1].state.write("OFF")
    #scope.commands.ch[1].scale.write(2)
    #scope.commands.ch[1].offset.write(34)
    scope.commands.display.waveview1.ch[2].state.write("ON")
    scope.commands.ch[2].scale.write(0.1)
    scope.commands.ch[2].offset.write(target_current)
    scope.commands.display.waveview1.ch[3].state.write("ON")
    scope.commands.ch[3].scale.write(1)
    scope.commands.ch[3].offset.write(target_output)
    scope.commands.display.waveview1.ch[4].state.write("off")

    scope.commands.horizontal.scale.write(0.1)

    scope.commands.display.specview1.viewstyle.write("OVErlay")

    set_falling_edge_trigger(3, minimum_allowable)
    set_peak_to_peak_measurement(3)
    #wait for scope to settle
    time.sleep(5)

    scope.write("ISplay:SPECView1:VIEWStyle OVErlay")
    print(scope.query("MEASUrement:MEAS1:RESUlts:CURRentacq:MAXimum?"))

    scope.write('SEARCH:ADDNEW “SEARCH1”')
    time.sleep(0.5)
    scope.write("SEARCH:SEARCH1:TRIGGER:A:EDGE:SLOPE RISE")
    scope.write("SEARCH:SEARCH1:TRIGGER:A:EDGE:SOURCE CH3")
    scope.write("SEARCH:SEARCH1:TRIGger:A:EDGE:THReshold {}".format(maximum_allowable))

    scope.write('SEARCH:ADDNEW “SEARCH2”')
    time.sleep(0.5)
    scope.write("SEARCH:SEARCH2:TRIGGER:A:EDGE:SLOPE FALL")
    scope.write("SEARCH:SEARCH2:TRIGGER:A:EDGE:SOURCE CH3")
    scope.write("SEARCH:SEARCH2:TRIGger:A:EDGE:THReshold {}".format(minimum_allowable))

    scope.write('SEARCH:ADDNEW “SEARCH3”')
    time.sleep(0.5)
    scope.write("SEARCH:SEARCH3:TRIGGER:A:EDGE:SLOPE FALL")
    scope.write("SEARCH:SEARCH3:TRIGGER:A:EDGE:SOURCE CH2")
    scope.write("SEARCH:SEARCH3:TRIGger:A:EDGE:THReshold {}".format(min_input_cur))
    scope.write("ACTONEVent:SEARCH:ACTION:SAVEIMAGe:STATE ")
    scope.write('SAVEONEVENT:FILENAME "{}"'.format(file_base_name))

    time.sleep(0.5)
    scope.write('SEARCH:ADDNEW “SEARCH4”')
    scope.write("SEARCH:SEARCH4:TRIGGER:A:EDGE:SLOPE RISE")
    scope.write("SEARCH:SEARCH4:TRIGGER:A:EDGE:SOURCE CH2")
    scope.write("SEARCH:SEARCH4:TRIGger:A:EDGE:THReshold {}".format(max_input_cur))
    scope.write("ACTONEVent:SEARCH:ACTION:SAVEIMAGe:STATE ON")
    scope.write('SAVEONEVENT:FILENAME "{}"'.format(file_base_name))
    #print(scope.query("MEASUrement:MEAS1:RESUlts:ALLAcqs:PK2PK?"))

    scope.write("ACTONEVent:ENable 1")

rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')

#Put all channels in single mode
my_instrument.query('OUTP:PAIR OFF')

#Ensure output is off
#SWITCHTOCHANNEL0
my_instrument.query('INST 1')
my_instrument.query('OUTP 1')

file_base_name = "../Logs/"+file_base_name+".csv"
with open(file_base_name, mode='a') as file:
    file.write('CH1 PSU Output (V),CH1 PSU Output Avg (A),CH1 PSU Output Min (A),CH1 PSU Output Max (A)\n')
#set the time
BKP_9141.set_local_time(my_instrument)

#set datalogging to USB
my_instrument.query('INIT:DLOG')

##TEST 1 PAH300###
#set the current
my_instrument.query('CURR 3') #TARGET VALUE IS 5A
print("Current Limit: 7A")

#ENABLE POWER
my_instrument.query('OUTP 1')
try:
    while (True):
        BKP_9141.improved_steady_state(my_instrument,file_base_name)
        # Pause for 5 seconds
        #time.sleep(time_step)

        #power off PSU
        #my_instrument.query('OUTP 0')
        #time.sleep(time_step)
except KeyboardInterrupt:
    print("exiting")
    #set datalogging to USB

    my_instrument.query('ABORt:DLOG')
    my_instrument.query('OUTP 0')

except Exception as error_code:
    print(error_code)
    my_instrument.query('ABORt:DLOG')
    my_instrument.query('OUTP 0')