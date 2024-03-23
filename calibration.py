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
    
#hardcoded freq, hardcoded delay, starts triggering
def startTriggerSRS():
    delays = {"T0":"1", "A":"2", "B":"3", "C":"5", "D":"6"}

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

#grabParam for generating waveform plot
def grabParam():
    global timeScale, timeStart, verticalScale, verticalOffset, verticalPosition
    print(queryOscCmd('wfmoutpre:xincr?'))
    timeScale = float(queryOscCmd('wfmoutpre:xincr?'))
    timeStart = float(queryOscCmd('wfmoutpre:xzero?'))
    verticalScale = float(queryOscCmd('wfmoutpre:ymult?')) # volts / level
    verticalOffset = float(queryOscCmd('wfmoutpre:yzero?')) # reference voltage
    verticalPosition = float(queryOscCmd('wfmoutpre:yoff?')) # reference position (level)

#establish settings for ANY WF acquisition
def estabOscSettings():
    #hardcoding settings [for now]
    channel = 'CH1'
    horScale = 'horScale'
    sampleRate = '10E-6'
    termination = '50E+0'
    vScale = '400E-6'
    triggerLvl = '60E-03'

    writeOscCmd(f'HORizontal:MODE:SCAle {horScale}}') #horizontal scale, each div (*10)
    #scope.write('HORizontal:MODE:RECOrdlength 20E+3')
    writeOscCmd(f'HORizontal:MODE:SAMPLERate {sampleRate}') #sampling rate, sample rate * hor. scale = RL
    writeOscCmd(f'MASK:MASKPRE:VSCAle {vScale}')
    writeOscCmd(f'{channel}:TERmination {termination}') #50E+0 vs 1E+0
    writeOscCmd(f"{channel}:BANdwidth:ENHanced OFF")
    writeOscCmd(f'{channel}:BANdwidth TWOfifty')
    writeOscCmd(f'{channel}:COUPling DC') #
    writeOscCmd(f'TRIGger:A:LEVel {triggerLvl}') #fixes trigger level

#establishes Math1, Math2, and Math settings
def estabOscFFTSettings():
    #hardcoding settings [for now]
    writeOscCmd('MATH1:NUMAVg 1000000') #sets math averages
    writeOscCmd('MATH2:NUMAVg 1000000') #sets math averages
    #scope.write('MATH2:SPECTral:MAG DBM')
    writeOscCmd('MATH2:SPECTral:MAG LINEAr') #sets units off of dB
    # r = scope.query('*opc?') # sync
    writeOscCmd('MATH2:VERTICAL:AUTOSCALE 0') #removes autoscaling so vert scale can be set
    writeOscCmd('MATH2:VERTICAL:SCALE 100') #sets math channel vertical scale
    #scope.write('MATH2:SPECTral:CENTER 30e6')
    r = queryOscCmd('*opc?') 
    #scope.write('MATH2:SPECTral:SPAN 5E6')
    r = queryOscCmd('*opc?') 
    writeOscCmd('MATH2:VERTical:POSition -4')
    writeOscCmd('MATH2:SPECTral:WINdow KAISERBessel') #multiplying all gate data by one
    writeOscCmd('MATH2:SPECTral:GATEWIDTH 100E-6') #setting math waveform gate width
    writeOscCmd('MATH2:SPECTral:GATEPOS 0') #controls FFT gate position 

def standardWaveform():
    return

def userModeSetup():
    modeSRS = input("Would you like to trigger via SRS? Y/N: ")
    if modeSRS == 'Y':
        initializeSRS()
    fourierTransform = input("Would you like to fourier transform? Y/N: ")
    if fourierTransform == 'Y':
        whereFT = input("Scope or PC based FFT? S/PC: ")
        if whereFT == 'S':
            acquireFT()
        elif whereFT == 'PC':
            acquirePCFT()

#acquire waveform
def acquireWF():
    return

#curvestream
def contAcqWF():
    return

#acquire FFT on scope (mathSpectralMag)
def acquireFT():
    estabOscFFTSettings()

    return

#PC based FFT acquisition
def acquirePCFT():
    return

#scales time values after acquisition
def scaleTime(timeValues):
    return

#scales waveform values after acquisition
def scaleWave(waveValues):
    return

#generate plot at termination of command
def generatePlot(xWave, yWave):
    plt.plot(xWave, yWave)
    plt.title("FFT Data")
    plt.xlabel("Intensity")
    plt.ylabel("Frequency")
    return


#probably write the initializing into a function where you can use "try:"

initializeScope()
initializeSRS()
grabParam()
userModeSetup()

