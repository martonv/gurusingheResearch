import serial
from serial.tools import list_ports
import time
#from serial import SerialException

delay = 0.1
port_name = "COM3"

class VSerialPort(serial.Serial):
    def __init__( self, portParam = None):
        serial.Serial.__init__(self)
        # try:
        self.baudrate = 921600
        self.timeout = 3
        self.port = port_name
        self.open()
        self.setDTR(False)
        self.flushInput()
        self.setDTR(True)
        self.write(b'ID?\r')
        response_bytes = self.read(1024) #total bytes expected back from return
        print(response_bytes)

        print(f"Serial port {port_name} opened successfully.")
        time.sleep(1.0)
        # except self.SerialException as e:
        #     print(f"Error opening serial port: {e}")
        

connect = VSerialPort('COM3')

def writeCommand(cmd):
    formatCmd = f"{cmd}"
    connect.reset_input_buffer()

    #testing with query, splitting strings to do so
    splitCmd = formatCmd.replace('<', ' ')
    queryCmd = splitCmd.split(' ')[0] + '?\r'
    print(queryCmd)
    connect.write(queryCmd.encode())
    time.sleep(delay)
    response_bytes = connect.read(1024)
    response = response_bytes.decode().strip()
    print(response)

    #then ready to send cmd
    formatCmd += "\r" 
    connect.reset_input_buffer()
    print(formatCmd)
    connect.write(formatCmd.encode())
    time.sleep(delay)
    response_bytes = connect.read(1024)
    response = response_bytes.decode().strip()
    print(response)

print("Select mode: ")
print("1) Single")
print("2) Sweep")
mode = input("1 or 2?")
match mode:
    case "1":
        writeCommand("MODe CW ")
    case "2":
        writeCommand("MODe SWEep ")

#single mode
if mode == "1":
    #frequency settings
    freq = input("Set new frequency? Y/N: ")
    if freq == "Y":
        newFreq = input("Set freq in MEGAHERTZ: ")
        writeCommand(f"Frequency {newFreq}M")

    step = input("Enter new step size? Y/N: ")
    if step == "Y":
        stepSize = input("Enter new step size in MEGAHERTZ: ")
        writeCommand(f"STEP {stepSize}M")

    #Adjust frequency by step freq
    freqInc = input("Change Step Frequency by STEP size?: Y/N: ")
    if freqInc == "Y":
        freqIncMode = input("Increment or decrement?: I/D: ")
        match freqIncMode:
            case "I":
                writeCommand("FrequencyINCrement")
            case "D":
                writeCommand("FrequencyDECrement")

    #Offset            
    offSet = input("Add offset? Default 0, Y/N: ")
    if offSet == "Y":
        newOffSet = input("Enter new offset in MEGAHERTZ: ")
        writeCommand(f"OFFset {newOffSet}M")

    #spur mode
    # SDN command has four spur mitigation modes. LN1=Lowest phase noise default mode,
    # LN2=Low phase noise reduced spur, LS1=low-spur mode, LS2= Lowest spur mode with higher
    # phase noise. 
    spur = ("Change spur mode? Y/N: ")
    if spur == "Y": 
        print("SDN command has four spur mitigation modes. LN1=Lowest phase noise default mode, LN2=Low phase noise reduced spur, LS1=low-spur mode, LS2= Lowest spur mode with higher phase noise.")
        type = input("Select spur mode: LN1, LN2, LS1, LS2")
        writeCommand(f"SND {type}")

    #AM modulation
    amMod = input("Enable AM Modulation? Default is 0, Y/N: ")
    if amMod == "Y":
        amModDB = input("What dB? Any value other than 0: ")
        writeCommand(f"AMD{amModDB}")
        amFreq = input("What frequency? Resolution in HERTZ: ")
        writeCommand(f"AMF{amFreq}")

    #rfLevel / power level
    rfLevel = input("Adjust RF Level? Y/N: ")
    if rfLevel == "Y":
        rfLevelVal = input("RF Level in Db/M: ")
        writeCommand(f"PoWeR{rfLevelVal}")
    
    #reference frequency: external reference frequency
    refFreq = input("Adjust reference frequency? Y/N: ")
    if refFreq == "Y":
        refFreqVal = input("Reference frequency in MEGAHERTZ: ")
        writeCommand(f"REFerence {refFreqVal}M")
    
