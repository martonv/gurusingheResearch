#testing for rotational transitions in the 12-13GHz range
#user input 0: start freq
#user input 1: freq step size
#user input 2: avg per freq step 
#user input 3: MW pulse width = 200ns
#user input 4: end freq


from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply
import time
import serial
from serial.tools import list_ports
import time
import pyvisa

valonPort = 'COM3'
zaberPort = 'COM4'
srsAddress = 'GPIB0::9::INSTR'
delay = 0.1

#connect valon
class VSerialPort(serial.Serial):
    def __init__( self, portParam = None):
        serial.Serial.__init__(self)
        # try:
        self.baudrate = 921600
        self.timeout = 3
        self.port = valonPort
        self.open()
        self.setDTR(False)
        self.flushInput()
        self.setDTR(True)
        self.write(b'ID?\r')
        response_bytes = self.read(1024) #total bytes expected back from return
        print(response_bytes)
        print(f"Serial port {valonPort} opened successfully.")
        time.sleep(1.0)

connectValon = VSerialPort('COM3')

#write command to valon
def writeCommandValon(cmd):
    formatCmd = f"{cmd}"
    connectValon.reset_input_buffer()

    #testing with query, splitting strings to do so
    splitCmd = formatCmd.replace('<', ' ')
    queryCmd = splitCmd.split(' ')[0] + '?\r'
    print(queryCmd)
    connectValon.write(queryCmd.encode())
    time.sleep(delay)
    response_bytes = connectValon.read(1024)
    response = response_bytes.decode().strip()
    print(response)

    #then ready to send cmd
    formatCmd += "\r" 
    connectValon.reset_input_buffer()
    print(formatCmd)
    connectValon.write(formatCmd.encode())
    time.sleep(delay)
    response_bytes = connectValon.read(1024)
    response = response_bytes.decode().strip()
    print(response)

#connecting SRS DG535
def connectSRS(srsAddress):
    global inst
    rm = pyvisa.ResourceManager('')
    rm.list_resources()

    inst = rm.open_resource(srsAddress)
    print(inst.write('IS'))
    
#writing command SRS DG535
def commandSRS(srsCmd):
    print("Sending ", srsCmd)
    returned = inst.write(srsCmd)
    print(returned)



#initializing Valon+SRS
print("Connecting to Valon - Standard COM3")
connectValon = VSerialPort('COM3')
writeCommand("ID?")
print("Done!")
print("Connecting to SRS... Address: ", srsAddress)
connectSRS(srsAddress)
print("Done!")

#valon inputs
valFreq = input("Enter Valon starting frequency (MHz): ")
valEndFreq = input("Enter Valon ending frequency (MHz): ")
valStepFreq = input("Enter Valon Freq. step size: ")
writeCommandValon("MODe CW ")
writeCommandValon("Frequency {valFreq}M")
writeCommandValon("STEP {valStepFreq}M")

#srs inputs
#sets trig to INT
commandSRS("TM 0")

#delays C, 5 by D, 6 + 0.000001s
commandSRS("DT 5,6,1E-6")

#zaber error catch
def zaberCommandCheck(reply):
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
        print(reply)
        return True

#zaber controls + inputs
#add in maximum distance error catch
with AsciiSerial(zaberPort) as port:
    zaber = AsciiDevice(port, 1)
    print("Current position: ", int(zaber.get_position())/20997, " mm")

    sendHome = input("Send to home (0 pos)? Y/N: ")
    if sendHome == "Y":
        reply = zaber.home()
        zaberCommandCheck(reply)
    changeVel = input("Change velocity? Y/N: ")
    if changeVel == "Y":
        changeVelVal = input("Enter new velocity in mm: ")
        reply = zaber.move_vel(changeVelVal)
        zaberCommandCheck(reply)

    absOrRel = input("Change starting position? abs/rel: ")
    if absOrRel == "abs":
        absDist = input("New absolute position (mm): ")
        reply = zaber.move_abs(absDist*20997)
        zaberCommandCheck(reply)
    if absOrRel == "rel":
        relDist = input("Move by relative dist. (mm): ")
        reply = zaber.move_vel(relDist*20997)
        zaberCommandCheck(reply)
    
    
    



    


