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

class SRSpyvisa(srsAddress):
    def __init__(self, address):
        self.address = address
        self.rm = pyvisa.Resourcemanager('')
        self.instr = self.rm.open_resource(self.address)



connectSRS = SRSpyvisa(srsAddress)
connectValon = VSerialPort('COM3')

#write command to valon
def writeCommand(cmd):
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

print("Connecting to Valon - Standard COM3")
connectValon = VSerialPort('COM3')
writeCommand("ID?")
print("Connecting to SRS...")


    


