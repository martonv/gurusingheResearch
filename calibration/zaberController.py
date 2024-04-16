#for zaber:
from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply
import time

#first, intialize from main
#then, use functions as needed

#initialize zaber as global
def initializeZaber():
    global zaberDevice
    port = AsciiSerial("COM4")
    zaberDevice = AsciiDevice(port, 1)
    print("________________________________")
    print("Zaber initialized at port: ", port)
    print("________________________________")
    return zaberDevice

#sends Zaber to home (0mm)     
def homeZaber():
    zaberDevice.home()

#moves Zaber to abs pos
def moveToZaber(pos):
    zaberDevice.move_abs(pos)
    currPos = zaberDevice.get_position()
    print("Zaber is at position: ")

#moves by relative pos, or distance from curr pos
def moveByZaber(dist):
    zaberDevice.move_abs(dist)
    currPos = zaberDevice.get_position()
    print(f"Zaber is at position: {currPos}")

def zaberSetup(startPosZaber, travelDistZaber):
    zaberDevice.move_abs(startPosZaber)
    zaberDevice.send(f"/set limit.max {travelDistZaber}")

#initializes movement at speed
def zaberStart(zaberSpeed):
    zaberDevice.move_vel(zaberSpeed)

def zaberSetMoveSpeed(zaberSpeed):
    return


