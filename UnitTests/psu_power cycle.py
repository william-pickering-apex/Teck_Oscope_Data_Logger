import pyvisa
import time
import BKP_9141

rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')





my_instrument.query('INST 2')
my_instrument.query('OUTP 0')


time.sleep(10)





my_instrument.query('INST 2')
my_instrument.query('OUTP 1')