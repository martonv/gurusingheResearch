import time
import pyvisa as visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import inquirer

#notes:
#ESR giving command error "5": Command Error. Shows that an error occurred while the
# instrument was parsing a command or query.

visa_address_Scope = 'TCPIP0::169.254.23.223::inst0::INSTR'
visa_address_SRS = 'GPIB0::9::INSTR'

channel = 'CH1'

#initializing scope
def initializeScope():
    global oscilloScope
    rm = visa.ResourceManager()
    oscilloScope = rm.open_resource(visa_address_Scope)
    oscilloScope.timeout = 10000 #ms
    oscilloScope.encoding = 'latin_1'
    oscilloScope.read_termination = '\n'
    oscilloScope.write_termination = None
    oscilloScope.write('*rst') #reset
    time.sleep(3)
    r = oscilloScope.query('*opc?') # sync
    print(r)
    oscilloScope.write('*cls')

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
    oscilloScope.write(command)
    errorCheck = oscilloScope.write('*ESR?')
    #print(f'Command status register: {errorCheck}')
    oscilloScope.write('*cls')

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
    global channel, horScale, sampleRate, termination, vScale, triggerLvl

    #hardcoding settings [for now]
    channel = 'CH1'
    horScale = 'horScale'
    sampleRate = '10E-6'
    termination = '50E+0'
    vScale = '400E-6'
    triggerLvl = '60E-03'

    writeOscCmd(f'HORizontal:MODE:SCAle {horScale}') #horizontal scale, each div (*10)
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
    global mathChannel

    #hardcoding settings for now 
    mathChannel = 'MATH2'
    mathAverages = '1000000'
    unitType = 'LINEAr'
    autoScale = '0'
    vScale = '100'
    centerFreq = '30E6'
    vSpan = '5E6'
    vertPos = '-4'
    windowType = 'KAISERBessel'
    gateWidth = '100E-6'
    gatePos = '0'
    channel = 'CH1'
    horScale = 'horScale'
    sampleRate = '10E-6'
    termination = '50E+0'
    vScale = '400E-6'
    triggerLvl = '60E-03'

    #establish math
    writeOscCmd(f'{mathChannel}:DEFINE "SpectralMag(AVG({channel}))"')
    writeOscCmd(f'SELECT:{mathChannel} 1')
    print('testFF')

    writeOscCmd(f'HORizontal:MODE:SCAle {horScale}') #horizontal scale, each div (*10)
    #scope.write('HORizontal:MODE:RECOrdlength 20E+3')
    writeOscCmd(f'HORizontal:MODE:SAMPLERate {sampleRate}') #sampling rate, sample rate * hor. scale = RL
    writeOscCmd(f'MASK:MASKPRE:VSCAle {vScale}')
    writeOscCmd(f'{channel}:TERmination {termination}') #50E+0 vs 1E+0
    writeOscCmd(f"{channel}:BANdwidth:ENHanced OFF")
    writeOscCmd(f'{channel}:BANdwidth TWOfifty')
    writeOscCmd(f'{channel}:COUPling DC') #
    writeOscCmd(f'TRIGger:A:LEVel {triggerLvl}') #fixes trigger level

    #hardcoding settings [for now]
    writeOscCmd(f'{mathChannel}:NUMAVg {mathAverages}') #sets math averages
    writeOscCmd(f'{mathChannel}:NUMAVg {mathAverages}') #sets math averages
    #scope.write('MATH2:SPECTral:MAG DBM')
    writeOscCmd(f'{mathChannel}:SPECTral:MAG {unitType}') #sets units off of dB
    # r = scope.query('*opc?') # sync
    writeOscCmd(f'{mathChannel}:VERTICAL:AUTOSCALE {autoScale}') #removes autoscaling so vert scale can be set
    writeOscCmd(f'{mathChannel}:VERTICAL:SCALE {vScale}') #sets math channel vertical scale
    #writeOscCmd('MATH2:VERTICAL:AUTOSCALE 0')
    writeOscCmd(f'MATH2:SPECTral:CENTER {centerFreq}')
    r = queryOscCmd('*opc?') 
    #writeOscCmd(f'MATH2:SPECTral:SPAN {vSpan}')
    r = queryOscCmd('*opc?') 
    writeOscCmd(f'{mathChannel}:VERTical:POSition {vertPos}')
    writeOscCmd(f'{mathChannel}:SPECTral:WINdow {windowType}') #multiplying all gate data by one
    writeOscCmd(f'{mathChannel}:SPECTral:GATEWIDTH {gateWidth}') #setting math waveform gate width
    writeOscCmd(f'{mathChannel}:SPECTral:GATEPOS {gatePos}') #controls FFT gate position 
    #writeOscCmd('TRIGger:A:LEVel 60e-03')
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

#
def fftWaveformAcq():

    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPBINARY')
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

#curvestream
def contAcqWF():
    return

#get x and y vals from FFT waveform
def scaleFFT(waveValues):
    fftYValues = np.array(waveValues, dtype='float')
    fftXValues = np.linspace(timeStart, timeScale*len(waveValues), len(waveValues), endpoint=False)
    return fftXValues, fftYValues

#PC based FFT acquisition
def acquirePCFT():
    return

#scales time values after acquisition
def scaleTime():
    totalTime = timeScale * recordLength
    timeStop = timeStart + totalTime
    scaledTime = np.linspace(0, timeStop, num=recordLength, endpoint=False)
    return scaledTime

#scales waveform values after acquisition
def scaleWave(waveValues):
    unscaled_wave = np.array(waveValues, dtype='float')
    scaled_wave = (unscaled_wave - verticalPosition) * verticalScale + verticalOffset
    return scaled_wave

#pc based FFT via numpy
def fft(yValues):
    yFFT = np.abs(np.fft.fft(yValues))
    xFFT = np.abs(np.fft.fftfreq(recordLength, timeScale))
    return xFFT, yFFT

#generate plot at termination of command
def generatePlot(xWave, yWave):
    plt.plot(xWave, yWave)
    plt.title("Data")
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.show()
    return

def contAcq():
    return

def mode():
    global answers
    questions = [
    inquirer.List('mode',
                  message='What mode would you like to enter:',
                  choices=['Waveform/PCFFT', 'FFTWF', 'ContWF', 'ContFFT'])
    ]

    answers = inquirer.prompt(questions)
    return answers


#if called, this function runs wf from scope and fft on PC
def waveformPCFFT():
    estabOscSettings()
    grabParam()

    #normal acq
    waveValues = standardWaveformAcq()

    #fft on pc of normal acq
    fftXValues, fftYValues = fft(waveValues)

    #scaling values to param
    scaledWave = scaleWave(waveValues)
    scaledTime = scaleTime()

    # plotting normal acq, normal acq FFT via PC
    generatePlot(scaledTime, scaledWave)
    generatePlot(fftXValues, fftYValues)


def main():
    initializeScope()
    initializeSRS()
    modeSetting = mode()
    
    match modeSetting:
        case 'Waveform/PCFFT':
            waveformPCFFT()

    # modeSRS = input("Would you like to trigger via SRS? Y/N: ")
    # if modeSRS == 'Y':
    #     initializeSRS()
    # fourierTransform = input("Would you like to fourier transform? Y/N: ")
    # if fourierTransform == 'Y':
    #     whereFT = input("Scope or PC based FFT? S/PC: ")
    #     if whereFT == 'S':
    #         acquireFT()
    #     elif whereFT == 'PC':
    #         xValues, yValues = standardWaveformAcq()
    #         acquirePCFT()
    # elif fourierTransform == 'N':
    #     standardWaveformAcq()




#probably write the initializing into a function where you can use "try:"

if __name__ == "__main__":
    main()
    t1 = threading.Thread(target=contAcq)
    t1.da
