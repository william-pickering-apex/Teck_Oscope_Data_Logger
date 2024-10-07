import pyvisa
import BKP_9141

rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')

#Put all channels in parallel mode for high current operation
my_instrument.query('OUTP:PAIR PARA3')

#Ensure output is off
my_instrument.query('OUTP 0')

file_base_name = "../Logs/"+input("Enter Test Name: ")+".csv"

#set the time
BKP_9141.set_local_time(my_instrument)

#set datalogging to USB
my_instrument.query('INIT:DLOG')

##TEST 1 PAH300###
#set the current
my_instrument.query('CURR 7') #TARGET VALUE IS 5A
print("Current Limit: 7A")

#ENABLE POWER
my_instrument.query('OUTP 1')
try:
    while (True):
        BKP_9141.battery_triangle_wave(my_instrument,file_base_name)
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