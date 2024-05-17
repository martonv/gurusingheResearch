import time
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import SRScontroller

#notes:
#ESR giving command error "5": Command Error. Shows that an error occurred while the
# instrument was parsing a command or query.

visa_address_Scope = 'TCPIP0::169.254.23.223::inst0::INSTR'
channel = 'CH1'


#initializing scope
def initializeScope():
    global oscilloScope
    rm = visa.ResourceManager()
    oscilloScope = rm.open_resource(visa_address_Scope)
    oscilloScope.timeout = 10000 #ms
    oscilloScope.encoding = 'latin_1'
    oscilloScope.read_termination = '\n'
    oscillowriteOscCmd_termination = None
    #oscillowriteOscCmd('*rst') #reset
    time.sleep(1)
    r = oscilloScope.query('*opc?') # sync
    print(r)
    oscilloScope.write('*cls')
    print("__________________________")
    print("Scope opened successfully.")
    print("__________________________")
    return oscilloScope


#sends command, ensures no error after
def writeOscCmd(command):
    oscilloScope.write(command)
    errorCheck = oscilloScope.write('*ESR?')
    #print(f'Command status register: {errorCheck}')
    oscilloScope.write('*cls')


#query command
def queryOscCmd(command):
    output = oscilloScope.query(f'{command}')
    #print(command, ": ", output)
    return output


#grabParam for generating waveform plot
def grabParam():
    print(queryOscCmd('wfmoutpre:xincr?'))
    timeScale = float(queryOscCmd('wfmoutpre:xincr?'))
    timeStart = float(queryOscCmd('wfmoutpre:xzero?'))
    verticalScale = float(queryOscCmd('wfmoutpre:ymult?')) # volts / level
    verticalOffset = float(queryOscCmd('wfmoutpre:yzero?')) # reference voltage
    verticalPosition = float(queryOscCmd('wfmoutpre:yoff?')) # reference position (level)
    print("______________________________")
    print("Parameters acquired from scope")
    print("______________________________")
    return timeScale, timeStart, verticalScale, verticalOffset, verticalPosition


#establish settings for ANY WF acquisition
def estabOscSettings():
    global channel, horScale, sampleRate, termination, vScale, triggerLvl

    #hardcoding settings [for now]
    channel = 'CH1'
    horScale = '5E-6'
    sampleRate = '100E+6'
    termination = '50E+0'
    vScale = '400E-6'
    triggerLvl = '60E-03'
    triggerSource = 'CH1'

    writeOscCmd(f'HORizontal:MODE:SCAle {horScale}') #horizontal scale, each div (*10)
    #writeOscCmd('HORizontal:MODE:RECOrdlength 20E+3')
    writeOscCmd(f'HORizontal:MODE:SAMPLERate {sampleRate}') #sampling rate, sample rate * hor. scale = RL
    writeOscCmd(f'MASK:MASKPRE:VSCAle {vScale}')
    writeOscCmd(f'{channel}:TERmination {termination}') #50E+0 vs 1E+0
    writeOscCmd(f"{channel}:BANdwidth:ENHanced OFF")
    writeOscCmd(f'{channel}:BANdwidth TWOfifty')
    writeOscCmd(f'{channel}:COUPling DC') #
    writeOscCmd(f'TRIGger:A:LEVel {triggerLvl}') #fixes trigger level
    writeOscCmd(f'TRIGGER:A:EDGE:SOURCE {triggerSource}') #sets trigger source


def estabMAXSettings(awgFreq):
    #setting up ch1
    writeOscCmd('CH1:TERMINATION 50.0E+0')

    #SETTING UP MATH
    writeOscCmd('MATH3:DEFINE "SpectralMag(CH1)"')
    writeOscCmd(f'MATH3:SPECTral:CENTER {awgFreq}E6')
    writeOscCmd('MATH3:SPECTral:SPAN 20E6')
    writeOscCmd(f'HORizontal:MODE:SCAle 500E-9')

    #cursor code
    writeOscCmd("CURSOR:STATE ON")
    writeOscCmd("CURSor:SOUrce1 MATH3")
    writeOscCmd("CURSor:SOURce2 MATH3")
    writeOscCmd(f"CURSor:VBArs:POS1 {awgFreq - 0.1}E+6") #cursor 1
    writeOscCmd(f"CURSor:VBArs:POS2 {awgFreq + 0.1}E+6") #cursor 2
    writeOscCmd("CURSOR:STATE ON")
    print(queryOscCmd("CURSor?"))

    #max set code
    writeOscCmd('MEASUREMENT:MEAS1:SOURCE1 MATH3')
    writeOscCmd('MEASUrement:MEAS1:TYPe MAXimum')
    writeOscCmd('MEASUrement:MEAS1:STATE ON')


def contAcqMAX():
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRIBINARY')
    writeOscCmd('data:source CH1')
    writeOscCmd('wfmoutpre:byt_n 1') 


#starts oscilloscope run
def oscCalibStart():
    # initial config
    writeOscCmd('acquire:state 0')
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRIBINARY')
    writeOscCmd('data:source CH1') # channel
    writeOscCmd('wfmoutpre:byt_n 1') # 1 byte per sample

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont
    writeOscCmd('acquire:state 1')


#stops oscilloscope run
def oscCalibStop():
    writeOscCmd('acquire:state 0')


def clearOsc():
    writeOscCmd("CLEAR ALL")


def oscRunScope():
    writeOscCmd('acquire:state 1') # run


#gas pulse acquisition
def acquireFFTDataAtMax(awgFreq):
    #math4 input param
    writeOscCmd('MATH4:DEFINE "SpectralMag(AVG(CH1))"')
    writeOscCmd('MATH4:SPECTral:MAG Linear')
    writeOscCmd(f'MATH4:SPECTral:CENTER {awgFreq}E6')
    writeOscCmd(f'SELECT:MATH4 1')
    writeOscCmd(f'HORizontal:MODE:SCAle 5E-6')

    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH4') # channel
    writeOscCmd('data:start 1') # first sample
    recordLength = int(queryOscCmd('horizontal:recordlength?'))
    writeOscCmd('data:stop {}'.format(recordLength))
    writeOscCmd('wfmoutpre:byt_nr 4')

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont acq
    writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1') # run

    # data query
    time.sleep(20)
    t7 = time.perf_counter()
    bin_wave = oscilloScope.query_binary_values('curve?', datatype='f', container=np.array, is_big_endian=True)
    t8 = time.perf_counter()
    print("acquire time: ", t8-t7)

    writeOscCmd('WFMOutpre?')

    return bin_wave



