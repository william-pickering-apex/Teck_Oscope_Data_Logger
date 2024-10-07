import pyvisa
import BKP_9141

rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')

#Put all channels in single mode
my_instrument.query('OUTP:PAIR OFF')

#Ensure output is off
my_instrument.query('OUTP 0')

file_base_name = "../Logs/"+input("Enter Test Name: ")+".csv"
with open(file_base_name, mode='a') as file:
    file.write('CH1 PSU Output (V),CH1 PSU Output Avg (A),CH1 PSU Output Min (A),CH1 PSU Output Max (A)\n')

#set the time
BKP_9141.set_local_time(my_instrument)

#set datalogging to USB
my_instrument.query('INIT:DLOG')

##TEST 4 PDQ10###
#set the current
my_instrument.query('CURR 1') #TARGET VALUE IS 5A
print("Current Limit: 1A")

#ENABLE POWER
my_instrument.query('OUTP 1')
try:
    while (True):
        print("Ramping Voltage from 20V to 34V")
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