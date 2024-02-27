import pyvisa

rm = pyvisa.ResourceManager('')
rm.list_resources()

inst = rm.open_resource('GPIB0::9::INSTR')

delays = {"T0":"1", "A":"2", "B":"3", "C":"5", "D":"6"}

while True:
    editDelays = input("Edit delays? Y/N:")
    if editDelays == "N":
        break
    elif editDelays == "Y":
        while True:
            delayVal = input("Which delay? T0,A,B,C,D: ")
            delayNext = input("Add to delay? T0,A,B,C,D: ")
            timeAdd = input("Add time (exponential, EX: 1.2E-6 is 1.2 microsec): ")
            try: 
                delayKey = delays[delayVal]
                delayAddition = delays[delayNext]
            except KeyError:
                print("Bad input!")
                continue
            else:
                delayStr = "DT " + delayKey + "," + delayAddition + "," + timeAdd
                print(delayStr)
                returned = inst.write(delayStr)
                break
    editDelays = input("Edit more delays? Y/N:")
    if editDelays == "N":
        break



# while True:
#     triggeringMode = input("Set triggering mode (EXT, INT): ")
#     if triggeringMode == 'EXT':
#         print('External triggering activated.')
#         while True:
#             try:
#                 volts = int(input("Set voltage threshold (V): "))
#             except ValueError:
#                 print("This is not a number.")
#                 continue
#             else:
#                 returned = inst.write("TM 1; TL " + str(volts))
#                 break
                
#         break


#         #inputDel = inst.write("DT ")
#     elif triggeringMode == 'INT':
#         while True:
#             try: 
#                 freq = float(input("Set frequency (hZ): "))
            
#             except ValueError:
#                 print("This is not an integer.")
#                 continue
#             else:
#                 break

#         print("Activating internal trigger at ", freq)
#         writeString = "TM 0; TR 0, " + str(freq)
#         returned = inst.write(writeString)
#         print(returned)
#         break

