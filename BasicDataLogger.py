from tm_devices.drivers import MSO6B, MSO4B
from tm_devices.helpers import PYVISA_PY_BACKEND
import time
from tm_devices import DeviceManager

file_base_name = input("Enter Test Name: ")
ch_count = 4
#ch_count = int(input("Enter Number of Channels: "))
#if ch_count > 4:
#    ch_count = 4
file_list=[None]*ch_count
for i in range(ch_count):
    file_list[i]="{}_CH{}.csv".format(file_base_name,i+1)
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
    scope.commands.ch[1].scale.write(10)
    scope.commands.display.waveview1.ch[2].state.write("ON")
    scope.commands.ch[2].scale.write(1)
    scope.commands.display.waveview1.ch[3].state.write("ON")
    scope.commands.ch[3].scale.write(10)
    scope.commands.display.waveview1.ch[4].state.write("ON")
    scope.commands.ch[4].scale.write(1)


    scope.commands.horizontal.scale.write(0.002)

    # Set horizontal record length to 20000
    #scope.commands.horizontal.scale.write(0.0004)

    ### Set horizontal position to 100
    #scope.commands.horizontal.position.write(10)
    try:
        while(True):
            for i in range(ch_count):
                with open(file_list[i], mode='a', newline='') as file:
                    #data_set =[0,0,0,0]
                    local_time = time.localtime()
                    file.write("{}:{}:{}".format(local_time.tm_hour,local_time.tm_min,local_time.tm_sec))
                    for i in range(1,ch_count+1):
                        for frame in scope.curve_query(i):
                            file.write("\n{}".format(frame))
    except KeyboardInterrupt:
        file.close()
        print("Exiting")