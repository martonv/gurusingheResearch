import serial
from serial import Serial

class VSerialPort( serial.Serial ):

    
    def __init__( self, portParam=None ):
        # Call the base constructor
        serial.Serial.__init__( self )

        self.port = 'COM3'
        self.timeout = 1.0
        self.open()
        self.baudrate = 921600

        self.write(b'ID\r')
        print(self.readall())

test = VSerialPort('COM3')
