from unittest.mock import DEFAULT

import pyvisa
import time

from numpy.f2py.auxfuncs import throw_error


def pull_current(my_instrument_in):
    my_instrument_in.write('MEASure:CURRent?')
    time.sleep(0.1)
    try:
        return float(my_instrument_in.read())
    except Exception:
        try:
            time.sleep(0.1)
            return float(my_instrument_in.read())
        except:
            return 0.0

def pull_voltage(my_instrument_in):
    my_instrument_in.write('MEASure:VOLTage?')
    time.sleep(0.1)
    try:
        return float(my_instrument_in.read())
    except Exception:
        try:
            time.sleep(0.1)
            return float(my_instrument_in.read())
        except:
            return 0.0

def pull_all(my_instrument_in):
    my_instrument_in.write('MEAS:ALL?')
    time.sleep(0.1)
    try:
        return float(my_instrument_in.read())
    except Exception:
        try:
            time.sleep(0.1)
            return float(my_instrument_in.read())
        except:
            return 0.0

def ave_pull_current(my_instrument_in, duration, time_step_in=0.1):
    pulls = int(duration/(0.1+time_step_in))-1
    if pulls <=0:
        pulls=0
        print("Only pulling an average of 1")
    ave_sample=pull_current(my_instrument_in)
    max_sample=ave_sample
    min_sample=ave_sample
    for i in range(pulls):
        time.sleep(time_step_in)
        current_sample=pull_current(my_instrument_in)
        ave_sample+=current_sample
        min_sample=min(min_sample,current_sample)
        max_sample=max(max_sample,current_sample)
    return [ave_sample/(pulls+1), min_sample, max_sample]

def battery_triangle_wave(my_instrument_in, csv_file_name,min_voltage=20,max_voltage=34):
    voltage_step=4
    time_at_voltage=20
    #CSV Format:
    #TIME, V, I_AVG, I_MIN, I_MAX
    try:
        with open(csv_file_name, mode='a') as file:
            #Step through the voltage range
            for i in range(5):
                #set the PSU output Voltage
                my_instrument_in.query('VOLT {}'.format(min(min_voltage+voltage_step*i,max_voltage)))
                for j in range(time_at_voltage):
                    print('Voltage Setpoint:{}'.format(pull_voltage(my_instrument_in)))
                    #Timestamp entry
                    local_time = time.localtime()
                    file.write("{}:{}:{},".format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))
                    sampled_current=ave_pull_current(my_instrument_in, 1)
                    file.write("{},{},{},{}\n".format(pull_voltage(my_instrument_in),sampled_current[0],sampled_current[1],sampled_current[2]))
    except Exception as error:
        file.close()
        raise

def set_local_time(my_instrument_in):
    local_time = time.localtime()
    # set date SYSTem:DATE <YY>,<MM>,<DD>
    my_instrument_in.query(
        'SYST:DATE {0:0>2},{1:0>2},{2:0>2}'.format(local_time.tm_year, local_time.tm_mon, local_time.tm_mday))
    # set time SYSTem:TIME <HH>,<MM>,<SS>
    my_instrument_in.query(
        'SYST:TIME {0:0>2},{1:0>2},{2:0>2}'.format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))


rm = pyvisa.ResourceManager()
rm.list_resources()

my_instrument = rm.open_resource('USB0::0x3121::0x0002::579I23132::INSTR')

#Put all channels in parallel mode for high current operation
my_instrument.query('OUTP:PAIR PARA3')

#Ensure output is off
my_instrument.query('OUTP 0')

file_base_name = "../Logs/"+input("Enter Test Name: ")+".csv"

#set the time
set_local_time(my_instrument)

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
        battery_triangle_wave(my_instrument,file_base_name)
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