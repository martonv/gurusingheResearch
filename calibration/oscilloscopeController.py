import time
import pyvisa as visa
import inquirer
import numpy as np

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
    time.sleep(3)
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
    global timeScale, timeStart, verticalScale, verticalOffset, verticalPosition
    print(queryOscCmd('wfmoutpre:xincr?'))
    timeScale = float(queryOscCmd('wfmoutpre:xincr?'))
    timeStart = float(queryOscCmd('wfmoutpre:xzero?'))
    verticalScale = float(queryOscCmd('wfmoutpre:ymult?')) # volts / level
    verticalOffset = float(queryOscCmd('wfmoutpre:yzero?')) # reference voltage
    verticalPosition = float(queryOscCmd('wfmoutpre:yoff?')) # reference position (level)
    print("__________________________")


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

def estabMAXSettings(cursor1, cursor2):
    #cursor code
    writeOscCmd("CURSOR:STATE ON")
    writeOscCmd("CURSor:SOUrce1 MATH1")
    writeOscCmd("CURSor:SOURce2 MATH1")
    writeOscCmd("CURSor:VBArs:POS1 29.9E+6")
    writeOscCmd("CURSor:VBArs:POS2 30.2E+6")
    writeOscCmd("CURSOR:STATE ON")
    print(queryOscCmd("CURSor?"))

    #max set code
    writeOscCmd('MEASUREMENT:MEAS1:SOURCE1 MATH1')
    writeOscCmd('MEASUrement:MEAS1:TYPe MAXimum')
    writeOscCmd('MEASUrement:MEAS1:STATE ON')
    

#establishes Math1, Math2, and Math settings
def estabOscFFTSettings():
    global mathChannel

    #hardcoding settings for now 
    mathChannel = 'MATH3'
    mathAverages = '1000000'
    unitType = 'Linear'
    autoScale = 'OFF'
    vScale = '100'
    centerFreq = '30E6'
    vSpan = '5E6'
    vertPos = '4'
    windowType = 'KAISERBessel'
    gateWidth = '100E-6'
    gatePos = '0'
    channel = 'CH1'
    #original settings
    horScale = '5E-6'
    sampleRate = '100E+6'
    termination = '50E+0'
    vScale = '400E-6'
    triggerLvl = '60E-03'
    triggerSource = 'CH1'

    #establish math
    writeOscCmd(f'{mathChannel}:DEFINE "SpectralMag({channel})"')
    writeOscCmd(f'{mathChannel}:SPECTral:MAG {unitType}')
    writeOscCmd(f'SELECT:{mathChannel} 1')
    r = queryOscCmd('*opc?') 

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

    #hardcoding settings [for now]
    writeOscCmd(f'{mathChannel}:NUMAVg {mathAverages}') #sets math averages
    #writeOscCmd('MATH2:SPECTral:MAG LINEAr')
    writeOscCmd(f'{mathChannel}:SPECTral:MAG {unitType}') #sets units off of dB
    #r = scope.query('*opc?') # sync
    writeOscCmd(f'{mathChannel}:VERTICAL:AUTOSCALE {autoScale}') #removes autoscaling so vert scale can be set
    writeOscCmd(f'{mathChannel}:VERTICAL:SCALE {vScale}') #sets math channel vertical scale
    writeOscCmd('MATH2:VERTICAL:AUTOSCALE 0')
    # writeOscCmd(f'MATH2:SPECTral:CENTER {centerFreq}')
    # r = queryOscCmd('*opc?') 
    # writeOscCmd(f'MATH2:SPECTral:SPAN {vSpan}')
    r = queryOscCmd('*opc?') 
    writeOscCmd(f'{mathChannel}:VERTical:POSition {vertPos}')
    writeOscCmd(f'{mathChannel}:SPECTral:WINdow {windowType}') #multiplying all gate data by one
    writeOscCmd(f'{mathChannel}:SPECTral:GATEWIDTH {gateWidth}') #setting math waveform gate width
    writeOscCmd(f'{mathChannel}:SPECTral:GATEPOS {gatePos}') #controls FFT gate position 
    writeOscCmd('TRIGger:A:LEVel 60e-03')

#
def standardWaveformAcq():
    global recordLength 
    #writeOscCmd('autoset EXECUTE') # autoset
    # t3 = time.perf_counter()
    # #r = queryOscCmd('*opc?') # sync
    # t4 = time.perf_counter()
    # print('autoset time: {} s'.format(t4 - t3))

    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRIBINARY')
    writeOscCmd('data:source CH1') # channel
    writeOscCmd('data:start 1') # first sample
    recordLength = int(queryOscCmd('horizontal:recordlength?'))
    writeOscCmd('data:stop {}'.format(recordLength)) # last sample
    writeOscCmd('wfmoutpre:byt_n 1') # 1 byte per sample

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:stopafter SEQUENCE') # single
    writeOscCmd('acquire:state 1') # run
    t5 = time.perf_counter()
    r = queryOscCmd('*opc?') # sync
    t6 = time.perf_counter()
    print('acquire time: {} s'.format(t6 - t5))

    #data query
    t7 = time.perf_counter()
    bin_wave = oscilloScope.query_binary_values('curve?', datatype='b', container=np.array)
    t8 = time.perf_counter()
    print('transfer time: {} s'.format(t8 - t7))

    writeOscCmd('WFMOutpre?')

    return bin_wave

#gets fft from scope (single)
def fftWaveformAcq():

    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH2') # channel
    writeOscCmd('data:start 1') # first sample
    recordLength = int(queryOscCmd('horizontal:recordlength?'))
    writeOscCmd('data:stop {}'.format(recordLength))
    writeOscCmd('wfmoutpre:byt_nr 4')

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:stopafter SEQUENCE') # single
    writeOscCmd('acquire:state 1') # run
    t5 = time.perf_counter()
    r = queryOscCmd('*opc?') # sync
    t6 = time.perf_counter()
    print('acquire time: {} s'.format(t6 - t5))

    # data query
    t7 = time.perf_counter()
    bin_wave = oscilloScope.query_binary_values('curve?', datatype='f', container=np.array, is_big_endian=True)
    t8 = time.perf_counter()

    writeOscCmd('WFMOutpre?')

    return bin_wave

def contAcqMAX():
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRIBINARY')
    writeOscCmd('data:source CH1')
    writeOscCmd('wfmoutpre:byt_n 1') 

#starts oscilloscope run
def oscCalibStart():
    writeOscCmd('acquire:state 0')
    writeOscCmd('header 0')
    #writeOscCmd('data:encdg FAStest')
    writeOscCmd('data:encdg SRIBINARY')
    writeOscCmd('data:source CH1') # channel
    # writeOscCmd('data:start 1') # first sample
    # recordLength = int(queryOscCmd('horizontal:recordlength?'))
    # writeOscCmd('data:stop {}'.format(recordLength)) # last sample
    writeOscCmd('wfmoutpre:byt_n 1') # 1 byte per sample

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont
    #writeOscCmd('DISplay:WAVEform OFF')
    #writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1')

#stops oscilloscope run
def oscCalibStop():
    writeOscCmd('acquire:state 0')

#curvestream
#encdg set to fastest
#display OFF will make it faster
def contAcqWF():

    #turn on settings
    #estabOscSettings()
    estabMAXSettings()

    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg FAStest')
    writeOscCmd('data:source CH1') # channel
    # writeOscCmd('data:start 1') # first sample
    # recordLength = int(queryOscCmd('horizontal:recordlength?'))
    # writeOscCmd('data:stop {}'.format(recordLength)) # last sample
    writeOscCmd('wfmoutpre:byt_n 1') # 1 byte per sample

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont
    #writeOscCmd('DISplay:WAVEform OFF')
    #writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1')


    while True:
        tx = time.perf_counter()
        bin_wave = oscilloScope.query_binary_values('curve?', datatype='b', container=np.array)
        fftYValues = np.array(bin_wave, dtype='float')
        print(max(bin_wave))
        ty = time.perf_counter()
        diff = ty-tx
        print(f'time: {diff}')
    #temp = oscilloScope.query_binary_values('curve?', datatype='b', container=np.array)

    # x = True
    # while x == True:
    #     bin_wave = oscilloScope.query_binary_values('curvestream?', datatype='b', container=np.array)
    #     temp = oscilloScope.query_binary_values('curve?', datatype='b', container=np.array)

    #     bin_wave = np.array(bin_wave, dtype='float')
    #     temp = np.array(temp, dtype='float')

    #     if bin_wave != temp:
    #         print(bin_wave)
    #     elif bin_wave == temp:
    #         x = False

#returns contFFT from scope
def contFFT():

    #turn on settings
    estabOscFFTSettings()

    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH2') # channel
    # writeOscCmd('data:start 1') # first sample
    # recordLength = int(queryOscCmd('horizontal:recordlength?'))
    # writeOscCmd('data:stop {}'.format(recordLength)) # last sample
    writeOscCmd('wfmoutpre:byt_n 4') # 1 byte per sample

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont
    #writeOscCmd('DISplay:WAVEform OFF')
    writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1') # run
    #writeOscCmd('curvestream?')
    # t5 = time.perf_counter()
    # r = queryOscCmd('*opc?') # sync
    # t6 = time.perf_counter()
    #print('acquire time: {} s'.format(t6 - t5))


def clearOsc():
    writeOscCmd("CLEAR ALL")


#gets mode from user for acq type
def mode():
    global answers
    questions = [
    inquirer.List('mode',
                  message='What mode would you like to enter:',
                  choices=['Waveform/PCFFT', 'FFTWF', 'ContWF', 'ContFFT'])
    ]

    answers = inquirer.prompt(questions)
    return answers
