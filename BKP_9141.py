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

def ave_pull_multi(my_instrument_in, duration, time_step_in=0.1,ch_count=3):
    pulls = int(duration/(0.1+time_step_in))-1
    if pulls <=0:
        pulls=0
        print("Only pulling an average of 1")
    return_values=list()
    for i in range(ch_count):
        my_instrument_in.query('INST {}'.format(i))
        ave_sample=pull_current(my_instrument_in)
        min_sample=ave_sample
        max_sample=ave_sample
        for i in range(pulls):
            time.sleep(time_step_in)
            current_sample=pull_current(my_instrument_in)
            ave_sample+=current_sample
            min_sample=min(min_sample,current_sample)
            max_sample=max(max_sample,current_sample)
        return_values.append(pull_voltage(my_instrument_in))
        return_values.append(ave_sample/(pulls+1))
        return_values.append(min_sample)
        return_values.append(max_sample)
    return return_values

def battery_triangle_wave(my_instrument_in, csv_file_name,min_voltage=24,max_voltage=34):
    voltage_step=4
    time_at_voltage=10
    #CSV Format:
    #TIME, V, I_AVG, I_MIN, I_MAX
    try:
        with open(csv_file_name, mode='a') as file:
            #Step through the voltage range
            for i in range(5):
                #set the PSU output Voltage
                my_instrument_in.query('VOLT {}'.format(min(min_voltage+voltage_step*i,max_voltage)))
                for j in range(time_at_voltage):
                    #Timestamp entry
                    local_time = time.localtime()
                    file.write("{}:{}:{},".format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))

                    #pull data
                    sampled_voltage = pull_voltage(my_instrument_in)
                    sampled_current=ave_pull_current(my_instrument_in, 1)

                    #write data to file on console
                    file.write("{},{},{},{}\n".format(sampled_voltage,sampled_current[0],sampled_current[1],sampled_current[2]))
                    print('Voltage Setpoint:{}V, Current Max:{}A'.format(sampled_voltage,sampled_current[2]))
            for i in range(5):
                #set the PSU output Voltage
                my_instrument_in.query('VOLT {}'.format(min(min_voltage+voltage_step*(5-i),max_voltage)))
                for j in range(time_at_voltage):
                    #Timestamp entry
                    local_time = time.localtime()
                    file.write("{}:{}:{},".format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))

                    #pull data
                    sampled_voltage = pull_voltage(my_instrument_in)
                    sampled_current=ave_pull_current(my_instrument_in, 1)

                    #write data to file on console
                    file.write("{},{},{},{}\n".format(sampled_voltage,sampled_current[0],sampled_current[1],sampled_current[2]))
                    print('Voltage Setpoint:{}V, Current Max:{}A'.format(sampled_voltage,sampled_current[2]))
    except Exception as error:
        file.close()
        raise

def improved_steady_state(my_instrument_in, csv_file_name,voltage_set=34):
    time_at_voltage=10
    #CSV Format:
    #TIME, V, I_AVG, I_MIN, I_MAX
    try:
        with open(csv_file_name, mode='a') as file:
            #Step through the voltage range
            #set the PSU output Voltage
            my_instrument_in.query('VOLT {}'.format(voltage_set))
            for j in range(time_at_voltage):
                #Timestamp entry
                local_time = time.localtime()
                file.write("{}:{}:{},".format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))

                #pull data
                sampled_voltage = pull_voltage(my_instrument_in)
                sampled_current=ave_pull_current(my_instrument_in, 1)

                #write data to file on console
                file.write("{},{},{},{}\n".format(sampled_voltage,sampled_current[0],sampled_current[1],sampled_current[2]))
                print('Voltage Setpoint:{}V, Current Max:{}A'.format(sampled_voltage,sampled_current[2]))

    except Exception as error:
        file.close()
        raise

def steady_state(my_instrument_in, csv_file_name,ch_count=3):
    voltage_step=4
    time_at_voltage=34
    #CSV Format:
    #TIME, V, I_AVG, I_MIN, I_MAX
    #try:
    with open(csv_file_name, mode='a') as file:
        #for j in range(time_at_voltage):
        #Timestamp entry
        local_time = time.localtime()
        file.write("{}:{}:{},".format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))

        #pull data
        for i in range(ch_count+1):
            my_instrument_in.query('INST {}'.format(i))
            sampled_current=ave_pull_multi(my_instrument_in, 1,0.1,ch_count)

        #print data
        output_string = ','.join([str(i) for i in sampled_current])
        file.write(output_string+'\n')
        print(output_string)

   # except Exception as error:
   #     file.close()
   #     raise

def set_local_time(my_instrument_in):
    local_time = time.localtime()
    # set date SYSTem:DATE <YY>,<MM>,<DD>
    my_instrument_in.query(
        'SYST:DATE {0:0>2},{1:0>2},{2:0>2}'.format(local_time.tm_year, local_time.tm_mon, local_time.tm_mday))
    # set time SYSTem:TIME <HH>,<MM>,<SS>
    my_instrument_in.query(
        'SYST:TIME {0:0>2},{1:0>2},{2:0>2}'.format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec))

