import pyvisa as visa

visa_address_SRS = 'GPIB0::9::INSTR'

#initializing SRS triggering
def initializeSRS():
    global SRS
    rm = visa.ResourceManager()
    SRS = rm.open_resource(visa_address_SRS)
    print("_______________________________________________________")
    print("SRS opened successfully... Switching to EXT Triggering.")
    print("_______________________________________________________")
    stopPulse()
    #turns on external trigger
    writeSRSCmd("TM 1; TL 1")

#hardcoded freq, hardcoded delay, starts triggering
#this is for future work, key:pair for controlling trigger delay
def startTriggerSRS():
    delays = {"T0":"1", "A":"2", "B":"3", "C":"5", "D":"6"}

#writes command to SRS
def writeSRSCmd(command):
    output = SRS.write(command)
    return output

#sets frequency and starts INT trigger for SRS trig (int)
def setFreq():
    global frequency
    frequency = float(input("Set frequency for triggering (hZ): "))
    print("Activating internal trigger at ", frequency)
    return frequency

def startTrig():
    writeString = "TR 0, " + str(frequency)
    writeSRSCmd(writeString)
    writeString = "TM 0"
    writeSRSCmd(writeString)
    print("Activating internal trigger at ", str(frequency))

def stopTrig():
    writeString = "TM 1; TL 1"
    writeSRSCmd(writeString)

def startPulse():
    writeString = "DT 3,2,100E-9"
    writeSRSCmd(writeString)

def stopPulse():
    writeString = "DT 3,2,0"
    writeSRSCmd(writeString)

def setTrig(freqIn):
    writeString = "TM 0; TR 0, " + str(freqIn)
    writeSRSCmd(writeString)
    print("Activating internal trigger at ", str(frequency))
