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

            print(f"Serial port {port_name} opened successfully.")
            time.sleep(1.0)
            # except self.SerialException as e:
            #     print(f"Error opening serial port: {e}")

    valonConnect = VSerialPort(port)
    
    return valonConnect

#write Valon cmds
def writeValonCommand(cmd):
    formatCmd = f"{cmd}"
    valonConnect.reset_input_buffer()

    #testing with query, splitting strings to do so
    # splitCmd = formatCmd.replace('<', ' ')
    # queryCmd = splitCmd.split(' ')[0] + '?\r'
    # print(queryCmd)
    # valonConnect.write(queryCmd.encode())
    # time.sleep(delay)
    # response_bytes = valonConnect.read(1024)
    # response = response_bytes.decode().strip()
    # print(response)

    #then ready to send cmd
    formatCmd += "\r" 
    valonConnect.reset_input_buffer()
    print(formatCmd)
    valonConnect.write(formatCmd.encode())
    time.sleep(delay)
    response_bytes = valonConnect.read(1024)
    response = response_bytes.decode().strip()
    print(response)

#valon settings init
def valonSettings():
    writeValonCommand("MODe CW ")

def valonStepUp():
    writeValonCommand("FrequencyINCrement")

def valonStepDown():
    writeValonCommand("FrequencyINCrement")