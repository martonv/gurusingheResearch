#for valon:
import serial
from serial.tools import list_ports
import time

delay = 0.1
port_name = "COM3"

def initializeValon(port):
    global valonConnect

    #creating class of valonConnection
    class VSerialPort(serial.Serial):
        def __init__( self, portParam = None):
            serial.Serial.__init__(self)
            # try:
            self.baudrate = 9600
            self.timeout = 3
            self.port = port_name
            self.open()
            self.setDTR(False)
            self.flushInput()
            self.setDTR(True)
            self.write(b'ID?\r')
            response_bytes = self.read(1024) #total bytes expected back from return
            print(response_bytes)
            #CW mode (continuous wave)
            print("________________________________________________________")
            print(f"Serial port for Valon: {port_name} opened successfully.")
            print("________________________________________________________")
            time.sleep(0.5)
            # except self.SerialException as e:
            #     print(f"Error opening serial port: {e}")

    valonConnect = VSerialPort(port)
    
    return valonConnect

#write Valon cmds, either writing or querying based on presence of \r
def writeValonCommand(cmd):
    #format command with line termination \r, encode (utf8 I think), send to Valon
    formatCmd = f"{cmd}"
    formatCmd += "\r" 
    valonConnect.reset_input_buffer()
    print(formatCmd)
    valonConnect.write(formatCmd.encode())
    time.sleep(delay)
    response_bytes = valonConnect.read(1024)
    response = response_bytes.decode().strip()
    print(response)
    #return response

#valon settings init
def valonSettings():
    writeValonCommand("MODe CW ")
    writeValonCommand("OEN 1")


def valonStepUp():
    writeValonCommand("FrequencyINCrement")

def valonStepDown():
    writeValonCommand("FrequencyINCrement")

def valonSettings():
    print("Establishing Valon Settings: ")

    currRF = writeValonCommand("PoWeR?")

    #set RFLevel, defaults to 1 in valonSettings
    rfLevel = input(f"Adjust RF Level? Currently: {currRF} | (Y/N): ")
    #turn on RF level
    writeValonCommand("PDN 1")
    if rfLevel == "Y":
        rfLevelVal = input("RF Level in Db/M: ")
        writeValonCommand(f"PoWeR{rfLevelVal}")
        writeValonCommand("PDN 1")

    #sets reference source, EXT is 1, INT is 0
    refSource = input("EXT or INT Reference Source? (INT/EXT): ")
    if refSource == "EXT":
        writeValonCommand("REFS 1")
    elif refSource == "INT":
        writeValonCommand("REFS 0")