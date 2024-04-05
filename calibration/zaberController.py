#for zaber:
from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply

#initialize zaber as global
def initializeZaber(portName):
    global zaberDevice
    port = AsciiSerial(portName)
    zaberDevice = AsciiDevice(port, 1)
    return zaberDevice

#sends Zaber to home (0mm)     
def homeZaber():
    zaberDevice.home()

initializeZaber("COM4")
reply = zaberDevice.home()
checkZaberCommand(reply)