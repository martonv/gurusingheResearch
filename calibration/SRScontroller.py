import pyvisa as visa

visa_address_SRS = 'GPIB0::9::INSTR'

#initializing SRS triggering
def initializeSRS():
    global SRS
    rm = visa.ResourceManager()
    SRS = rm.open_resource(visa_address_SRS)
    print("SRS opened successfully.")

#hardcoded freq, hardcoded delay, starts triggering
def startTriggerSRS():
    delays = {"T0":"1", "A":"2", "B":"3", "C":"5", "D":"6"}

#writes command to SRS
def writeSRSCmd(command):
    output = SRS.write(command)
    return output

def setFreq(freq):
    print("Activating internal trigger at ", freq)
    writeString = "TM 0; TR 0, " + str(freq)
    writeSRSCmd(writeString)