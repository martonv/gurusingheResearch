from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply
import time

# Helper to check that commands succeeded.
def check_command_succeeded(reply):
    """
    Return true if command succeeded, print reason and return false if command
    rejected

    param reply: AsciiReply

    return: boolean
    """
    if reply.reply_flag != "OK": # If command not accepted (received "RJ")
        print ("Danger! Command rejected because: {}".format(reply.data))
        return False
    else: # Command was accepted
        return True

# Open a serial port. You may need to edit this section for your particular
# hardware and OS setup.
#with AsciiSerial("/dev/ttyUSB0") as port:  # Linux
with AsciiSerial("COM4") as port:  # Windows

    # Get a handle for device #1 on the serial chain. This assumes you have a
    # device already in ASCII 115,220 baud mode at address 1 on your port.
    device = AsciiDevice(port, 1) # Device number 1
    
    # Home the device and check the result.
    # reply = device.home()
    # if check_command_succeeded(reply):
    #     print("Device homed.")
    # else:
    #     print("Device home failed.")
    #     exit(1)

    # # Make the device has finished its previous move before sending the
    # # next command. Note that this is unnecessary in this case as the
    # # AsciiDevice.home command is blocking, but this would be required if
    # # the AsciiDevice.send command is used to trigger movement.
    # device.poll_until_idle()

    # #in microSteps
    # vel = int(input("Set device velocity: "))*20997
    
    # # sets speed = input, waits on end travel before continuing
    # start_time = time.time()
    # print("Start time: ", )
    # response = device.move_vel(speed=vel, blocking=True)
    # print(time.time() - start_time)
    # print(response)
    # print("Done!")
    # reply = device.home()
    

    # distMM = int(input("Enter distance"))
    # print("Moving by steps: ", distMM)
    # distSteps = distMM*20997


    # # Now move the device to a non-home position.
    # reply = device.move_rel(distSteps) # move rel 2000 microsteps
    # print("Moving by ... ",distMM, " mm")
    # if not check_command_succeeded(reply):
    #     print("Device move failed.")
    #     exit(1)
        

    # # # Wait for the move to finish.
    # # device.poll_until_idle()

    # # Read back what position the device thinks it's at.

    # # Port is automatically cleaned up by 'with' statement above.\

    reply = device.home()
    if check_command_succeeded(reply):
        print("Device homed.")
    else:
        print("Device home failed.")
        exit(1)
    device.poll_until_idle()
    looper=True
    while looper == True:
        print("Welcome to Zaber Controller!")
        print("1) Get Position")
        print("2) Set Move Velocity")
        print("3) Move by relative distance")
        print("4) Move by absolute distance")
        print("5) Send Home")
        print("6) Quit")
        userIn = int(input("Make a selection #: "))
        match userIn:
            case 1: 
                print("Device position is now: ", int(device.get_position())/20997, " mm")
            case 2:
                vel = int(input("Set device velocity (mm): "))*20997
                print("Device position is now: ", int(device.get_position())/20997, " mm")
            case 3:
                distMM = int(input("Enter distance: "))
                print("Moving by steps: ", distMM*20997)
                distSteps = distMM*20997
                reply = device.move_rel(distSteps) # move rel 2000 microsteps
                print("Moving by ... ",distMM, " mm")
                if not check_command_succeeded(reply):
                    print("Device move failed.")
                    exit(1)
                print("Device position is now: ", int(device.get_position())/20997, " mm")
            case 4:
                distMM = int(input("Enter distance (mm): "))
                print("Moving by steps: ", distMM*20997)
                distSteps = distMM*20997
                reply = device.move_abs(distSteps) # move rel 2000 microsteps
                print("Moving by ... ",distMM, " mm")
                if not check_command_succeeded(reply):
                    print("Device move failed.")
                    exit(1)
                print("Device position is now: ", int(device.get_position())/20997, " mm")
            case 5:
                reply = device.home()
                if check_command_succeeded(reply):
                    print("Device homed.")
                    print("Device position is now: ", int(device.get_position())/20997, " mm")
                else:
                    print("Device home failed.")
                    exit(1)
            case _:
                looper = False






    