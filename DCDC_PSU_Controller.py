from unittest.mock import DEFAULT

import pyvisa
import time


def pull_current(my_instrument_in):
    my_instrument_in.write('MEASure:CURRent?')
    time.sleep(0.2)
    outputstr = my_instrument_in.query_ascii_values('MEASure:CURRent?')
    return (outputstr)

rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')

#SWITCH TO CHANNEL 0
print(my_instrument.query('INST 0'))
local_time = time.localtime()
#set date SYSTem:DATE <YY>,<MM>,<DD>
my_instrument.query('SYST:DATE {0:0>2},{1:0>2},{2:0>2}'.format(local_time.tm_year,local_time.tm_mon,local_time.tm_mday))
#set time SYSTem:TIME <HH>,<MM>,<SS>
my_instrument.query('SYST:TIME {0:0>2},{1:0>2},{2:0>2}'.format(local_time.tm_hour,local_time.tm_min,local_time.tm_sec))
time_step = 20
#set datalogging to USB
my_instrument.query('INIT:DLOG')
def battTriWave():
    my_instrument.query('VOLT 20')
    print(pull_current(my_instrument))
    time.sleep(time_step)               
    my_instrument.query('VOLT 24')
    print(pull_current(my_instrument))
    time.sleep(time_step)               
    my_instrument.query('VOLT 28')
    print(pull_current(my_instrument))
    time.sleep(time_step)               
    my_instrument.query('VOLT 32')
    print(pull_current(my_instrument))
    time.sleep(time_step)               
    my_instrument.query('VOLT 34')
    time.sleep(time_step)               
    my_instrument.query('VOLT 32')
    time.sleep(time_step)               
    my_instrument.query('VOLT 28')
    time.sleep(time_step)               
    my_instrument.query('VOLT 24')
    time.sleep(time_step)               
    my_instrument.query('VOLT 20')
try:
    my_instrument.query('VOLT 28')
    my_instrument.query('OUTP 1')
    while (True):
        time.sleep(time_step)
        battTriWave()
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
