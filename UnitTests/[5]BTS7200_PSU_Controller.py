import pyvisa
import time
import BKP_9141

rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')

#Put all channels in single mode
my_instrument.query('OUTP:PAIR OFF')

#Ensure output is off
#SWITCHTOCHANNEL0
my_instrument.query('INST 0')
my_instrument.query('OUTP 0')
my_instrument.query('INST 1')
my_instrument.query('OUTP 0')
my_instrument.query('INST 2')
my_instrument.query('OUTP 0')


time.sleep(0.1)
#set the time
BKP_9141.set_local_time(my_instrument)

#set datalogging to USB
my_instrument.query('INIT:DLOG')

##TEST 4 PDQ10###
#set the current
print("Current Limit: 4A")

#ENABLE POWER CH0
my_instrument.query('INST 0')
my_instrument.query('VOLT 5')
my_instrument.query('CURR 4') #TARGET VALUE IS 3.6A
my_instrument.query('OUTP 1')

time.sleep(0.1)

file_base_name = "../Logs/"+input("Enter Test Name: ")+".csv"
with open(file_base_name, mode='a') as file:
    file.write('CH1 PSU Output (V),CH1 PSU Output Avg (A),CH1 PSU Output Min (A),CH1 PSU Output Max (A)')

print("Steady State Voltage at 5V")
try:
    while (True):
        BKP_9141.steady_state(my_instrument,file_base_name,2)

except KeyboardInterrupt:
    print("exiting")
    #set datalogging to USB

    my_instrument.query('ABORt:DLOG')
    my_instrument.query('OUTP 0')

#except Exception as error_code:
#    print(error_code)
#    my_instrument.query('ABORt:DLOG')
#    my_instrument.query('OUTP 0')