import time
import pyvisa as visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

visa_address_Scope = 'TCPIP0::169.254.23.223::inst0::INSTR'
visa_address_SRS = 'GPIB0::9::INSTR'

#initializing scope
def initializeScope():
    global oscilloScope
    rm = visa.ResourceManager()
    oscilloScope = rm.open_resource(visa_address_Scope)
    oscilloScope.timeout = 10000 #ms
    oscilloScope.encoding = 'latin_1'
    oscilloScope.read_termination = '\n'
    oscilloScope.write_termination = None
    #oscilloScope.write('*rst') #reset
    r = oscilloScope.query('*opc?') # sync

#initializing SRS triggering
def initializeSRS():
    global SRS
    rm = visa.ResourceManager()
    SRS = rm.open_resource(visa_address_SRS)

#sends command, ensures no error after
def writeOscCmd(command):
    oscilloScope.write(f'{command}')
    errorCheck = oscilloScope.write('*ESR?')
    print(f'Command status register: {errorCheck}')

#query command
def queryOscCmd(command):
    output = oscilloScope.query(f'{command}')
    print(command, ": ", output)
    return output

#writes command to Oscilloscope
def writeSRSCmd(command):
    output = SRS.write(command)
    return output

#generate plot at termination of command
def generatePlot(xWave, yWave):
    plt.plot(xWave, yWave)
    plt.title("FFT Data")
    plt.xlabel("Intensity")
    plt.ylabel("Frequency")
    return

#grabParam for generating waveform plot
def grabParam():
    global timeScale, timeStart, verticalScale, verticalOffset, verticalPosition
    print(queryOscCmd('wfmoutpre:xincr?'))
    timeScale = float(queryOscCmd('wfmoutpre:xincr?'))
    timeStart = float(queryOscCmd('wfmoutpre:xzero?'))
    verticalScale = float(queryOscCmd('wfmoutpre:ymult?')) # volts / level
    verticalOffset = float(queryOscCmd('wfmoutpre:yzero?')) # reference voltage
    verticalPosition = float(queryOscCmd('wfmoutpre:yoff?')) # reference position (level)

def estabOscSettings():
    writeOscCmd('HORizontal:MODE:SCAle 10E-6') #horizontal scale, each div (*10)
    #scope.write('HORizontal:MODE:RECOrdlength 20E+3')
    writeOscCmd('HORizontal:MODE:SAMPLERate 200E+6') #sampling rate, sample rate * hor. scale = RL
    #print(scope.query('HORIZONTAL:MODE:SAMPLERATE?'))
    writeOscCmd('HORizontal:MODE:SCAle 10E-6')
    writeOscCmd('MASK:MASKPRE:VSCAle 400E-6')
    writeOscCmd('CH1:TERmination 50E+0') #50E+0 vs 1E+0
    writeOscCmd("CH1:BANdwidth:ENHanced OFF")
    writeOscCmd('CH1:BANdwidth TWOfifty')
    writeOscCmd('CH1:COUPling DC') #
    writeOscCmd('MATH1:NUMAVg 1000000') #sets math averages
    writeOscCmd('MATH2:NUMAVg 1000000') #sets math averages
    writeOscCmd('MATH2:SPECTral:MAG DBM')
    # scope.write('MATH2:SPECTral:MAG LINEAr') #sets units off of dB
    # r = scope.query('*opc?') # sync
    writeOscCmd('MATH2:VERTICAL:AUTOSCALE 0') #removes autoscaling so vert scale can be set
    writeOscCmd('MATH2:VERTICAL:SCALE 100') #sets math channel vertical scale
    writeOscCmd('MATH2:SPECTral:CENTER 30E6')
    writeOscCmd('MATH2:SPECTral:SPAN 5E6')
    writeOscCmd('MATH2:VERTical:POSition -4')

def standardWaveform():
    return

def userModeSetup():
    mode = input("Would you like to trigger via SRS? Y/N:")
    if mode == 'Y':
        initializeSRS()


#probably write the initializing into a function where you can use "try:"
initializeScope()
initializeSRS()
grabParam()
userModeSetup()

