
import pyvisa
import time

from numpy.ma.core import append

rm = pyvisa.ResourceManager()
print(rm.list_resources())

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')
#SWITCH TO CHANNEL 0
my_instrument.query('INST 0')
my_instrument.query('OUTP 1')
time.sleep(1)
my_instrument.write('MEASure:CURRent?')
time.sleep(0.2)
outputstr=my_instrument.query_ascii_values('MEASure:CURRent?')
print(*outputstr)
time.sleep(1)
my_instrument.query('OUTP 0')