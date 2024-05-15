import time
import pyvisa as visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import valonController, oscilloscopeController, zaberController, SRScontroller

#get x and y vals from FFT waveform
def scaleFFT(waveValues):
    fftYValues = np.array(waveValues, dtype='float')
    fftXValues = np.linspace(oscilloscopeController.timeStart, oscilloscopeController.timeScale*len(waveValues), len(waveValues), endpoint=False)
    return fftXValues, fftYValues


#scales time values after acquisition
def scaleTime():
    totalTime = oscilloscopeController.timeScale * oscilloscopeController.recordLength
    timeStop = oscilloscopeController.timeStart + totalTime
    scaledTime = np.linspace(0, timeStop, num=oscilloscopeController.recordLength, endpoint=False)
    return scaledTime


#scales waveform values after acquisition
def scaleWave(waveValues):
    unscaled_wave = np.array(waveValues, dtype='float')
    scaled_wave = (unscaled_wave - oscilloscopeController.verticalPosition) * oscilloscopeController.verticalScale + oscilloscopeController.verticalOffset
    return scaled_wave


#pc based FFT via numpy
def fft(yValues):
    yFFT = np.abs(np.fft.fft(yValues))
    xFFT = np.abs(np.fft.fftfreq(oscilloscopeController.recordLength, oscilloscopeController.timeScale))
    return xFFT, yFFT


#generate plot at termination of command
def generatePlot(xWave, yWave):
    plt.plot(xWave, yWave)
    plt.title("Data")
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.show()
    return


#if called, this function runs wf from scope and fft on PC
def waveformPCFFT():
    oscilloscopeController.estabOscSettings()
    oscilloscopeController.grabParam()

    #normal acq
    waveValues = oscilloscopeController.standardWaveformAcq()

    #fft on pc of normal acq
    fftXValues, fftYValues = fft(waveValues)

    #scaling values to param
    scaledWave = scaleWave(waveValues)
    scaledTime = scaleTime()

    # plotting normal acq, normal acq FFT via PC
    generatePlot(scaledTime, scaledWave)
    generatePlot(fftXValues, fftYValues)


#gets fftWF from scope 
def fftFromScope():
    #estabOscSettings()
    oscilloscopeController.estabOscFFTSettings()
    oscilloscopeController.grabParam()

    #acquire waveform
    waveValues = oscilloscopeController.fftWaveformAcq()

    #acquire vals
    xValues, yValues = scaleFFT(waveValues)
    
    #plot values 
    #generatePlot(xValues, yValues)


#runs cont FFT from scope
def contFFTFromScope():
    oscilloscopeController.estabOscFFTSettings()
    oscilloscopeController.grabParam()

    #acquire waveform
    waveValues = oscilloscopeController.contFFT()

    #acquire vals
    xValues, yValues = scaleFFT(waveValues)

    #plot values 
    generatePlot(xValues, yValues)


#
def calibrationInit():
    global valonFreq, valonFreqStep, valonTotalSteps, startPosZaber, endPosZaber, speedZaber, oscCursor1, oscCursor2, trigFreq, moveVelMM, endDistZaberMM, startPosZaberMM


    #Valon config
    totalFreq = float(input("Starting frequency? (MHz): "))
    valonFreq = totalFreq - 100
    valonController.writeValonCommand(f"Frequency {valonFreq} M")
    # valonFreqStep = input("Freq step size? (MHz): ")
    # valonController.writeValonCommand(f"STEP {valonFreqStep}M")
    # valonTotalSteps = input("Calibrate until what frequency? (MHz): ")




    #Zaber config
    # setZaber = input("Setup Zaber? Y/N: ")
    # if setZaber == "Y":
    #sends zaber to 0mm
    zaberController.homeZaber()        
    #1mm = 20997.375 steps
    #1m/s = 3040.2099738 steps/s

    #setting zaber travel dist, initial start pos:
    while True: 
        try:
            #OLD, FIX ME
            #startPosZaber = float(input("Starting position? (mm): "))
            #endPosZaber = float(input("Ending position? (mm): "))
            
            #FIX ME *****************************************************************************************************************************
            #startPosZaber = ((4.23491632201815e-9*(totalFreq**2)) + (0.00214275759953761*totalFreq) - 2.05776365002228)
            #double for this since the first val taken out of midpt
            endPosZaber = 37
            startPosZaber = 36

            #global positions in MM for plotting
            startPosZaberMM = startPosZaber
            endDistZaberMM = endPosZaber

            print("Attempting to travel from ", startPosZaber, "mm to ", endPosZaber, "mm")
            if endPosZaber <= 40 and startPosZaber <= 40 and endPosZaber >= 0 and startPosZaber >= 0:
                endPosZaber = round(endPosZaber * 20997.375)
                startPosZaber = round(startPosZaber * 20997.375)
            elif endPosZaber < 0 or endPosZaber > 40 or startPosZaber < 0 or startPosZaber > 40:
                raise ValueError
            break
        except ValueError:
            print("Invalid integers somewhere. The numbers must be between 0 and 40mm.")

    #step size only needed for other approach
    #if you ADD IT BACK READD AS GLOBAL
    # while True: 
    #     try:
    #         stepSizeZaber = int(input("Step size between acquisitions? (mm, max 10mm): "))
    #         if stepSizeZaber <= 10:
    #             stepSizeZaber = round(stepSizeZaber * 20997.375)
    #         elif stepSizeZaber < 0 or stepSizeZaber > 10:
    #             raise ValueError
    #         break
    #     except ValueError:
    #         print("Invalid integer. The number must be between 0 and 10mm.")

    #speed for zaber
    while True:
        try:
            speedZaber = float(input("Set the movement velocity of the Zaber (mm/s, max 3.5m/s): "))
            moveVelMM = speedZaber
            if speedZaber <= 3.5 and speedZaber > 0:
                speedZaber = round(speedZaber * 34402.099737532773)
            elif speedZaber < 0 or speedZaber > 3.5:
                raise ValueError
            break
        except ValueError:
            print("Invalid integer. The number must be between 0 and 3.5mm.")

    zaberController.zaberSetup(startPosZaber, endPosZaber)

    #SRS config
    trigFreq = SRScontroller.setFreq()

    #osc cursor config
    
    # oscCursor1 = input("Enter cursor 1 bounds (MHz): ")
    # oscCursor2 = input("Enter cursor 2 bounds (MHz): ")


#start by triggering, runs zaber totality of 
def calibrateRun():
    global maxList, timeList
    maxList = []
    timeList = []

    oscilloscopeController.estabMAXSettings()

    startZaber = startPosZaber/20997
    print(f"Moving Zaber to {startZaber}.")
    zaberController.zaberDevice.poll_until_idle()

    #valonSteps = (float(valonTotalSteps) - float(valonFreq))/float(valonFreqStep) #check this with ranil, do we want to run twice if from 12005 to 12010?
    #zaberMoves = (endPosZaber - startPosZaber)/stepSizeZaber
    #valonCounter = 1

    #start osc run/acq
    oscilloscopeController.oscCalibStart()

    #starts trigger and thus calibration
    SRScontroller.startTrig()

    # while valonCounter <= valonSteps:
        
    oscilloscopeController.clearOsc()

    threadZaber = threading.Thread(target=zaberThread)
    threadAcquire = threading.Thread(target=acquireThread)
    #threads
    threads = [threadZaber, threadAcquire]

    #time based loop here acquiring based on trigFreq for entirity of zaber mvmt
    #pollUntilIdle() for zaber thread
    #acquire until done for acquireThread
    
    #loop to start and end threads together 
    for threadInstances in threads:
        threadInstances.start()

    for threadInstances in threads:
        threadInstances.join()

    #set max speed back to fast or this will be SLOW on SLOW MOVES

    zaberController.moveToZaber(startPosZaber)
    zaberController.zaberDevice.poll_until_idle()
    currPos = zaberController.zaberDevice.get_position()
    print("Homing... Zaber is at position: ", currPos/20997)
    zaberController.zaberDevice.poll_until_idle()

        # print("Current Valon Step: ", valonCounter)
        # print("Total steps remaining: ", valonSteps)
        # print("Steps remaining: ", int(valonSteps) - valonCounter)
        # valonCounter += 1

        #*******************************************LOOK HERE MARTON
        # VALON NEEDS TO STEP UP IF ACTUALLY RUNNING
        # valonController.valonStepUp()

    #stops osc acq
    oscilloscopeController.oscCalibStop()

    #cleanup this code and comment
    print("acq length: ", len(maxList))

    #timeTravel = (endDistZaberMM/moveVelMM) * int(valonSteps)
    #totalPos = timeTravel * moveVelMM

    #**********************
    #rewrite this code to iterate only after experiment completion
    #ie no embedded list because wont need it with 1 list val set 
    #**********************


    for maxLists in maxList:
        posArr = np.linspace(startPosZaberMM, endDistZaberMM, len(maxLists))
        print("Length of arr: ", len(maxList))
        print(max(maxLists))
        plt.plot(posArr, maxLists)
        plt.xlabel('Zaber Position (mm)')
        plt.ylabel('Intensity (Volts)')
        plt.show()
        print(max(maxLists))
    
    #print("calc time travel: ", timeTravel)

    #findPeakPos()

    for items in maxList:
        print("len: ", len(items))
        maxer = max(items)
        for index, values in enumerate(items):
            if values == maxer:
                print("Max position found: ", posArr[index])
                peakMax = posArr[index]

    print("Moving to maximum: ", peakMax)
    zaberController.moveToZaber(int(peakMax*20997))
    SRScontroller.stopTrig()
    SRScontroller.startPulse()
    SRScontroller.setTrig(5)

    counter = 0
    first = time.perf_counter()

    time.sleep(20)
    SRScontroller.stopTrig()
    # while counter >=20:
    #     counter = time.perf_counter() - first
    
    SRScontroller.stopPulse()
        

def findPeakPos():
    peak = len(maxList[0])
    zaberController.moveToZaber(peak)
    #plot code 

def zaberThread():
    global loopVar
    loopVar = 1
    timeZaberStart = time.perf_counter()
    totalTime = zaberController.zaberStart(speedZaber)
    zaberController.zaberDevice.poll_until_idle()
    timeZaberEnd = time.perf_counter()
    currPos = zaberController.zaberDevice.get_position()
    print("Zaber is at end position: ", currPos/20997, " mm")
    totalTimeZaber = timeZaberEnd - timeZaberStart
    print("Zaber move time (s): ", totalTimeZaber)
    loopVar = 0
    timeList.append(totalTimeZaber)
    return

#currently doesnt run based on triggerFreq, if required then use if/else with time.perfcounter()
def acquireThread():
    global loopVar
    tempMaxList = []
    while loopVar == 1:
        #currently we are not acquiring based on frequency 
        # currTime = time.time()
        # if time.time() - currTime >= float(1/trigFreq):
        tempMaxList.append(float(oscilloscopeController.queryOscCmd('MEASUrement:MEAS1:VALUE?')))
    
    maxList.append(tempMaxList)


# def startNStop():
#     oscilloscopeController.grabParam()
#     oscilloscopeController.estabOscFFTSettings()
#     SRScontroller.startTrig()
#     oscilloscopeController.contFFT()
    
#     valonSteps = (valonTotalSteps - valonFreq)/valonFreqStep
#     zaberMoves = (endPosZaber - startPosZaber)/stepSizeZaber
#     valonCounter = 1

#     # while valonCounter <= valonSteps:
        
#     #     for zaberMvmts in range(1, zaberMoves+1):
            
#     #         #first, move zaber by step size
#     #         zaberController.moveByZaber(stepSizeZaber)

#     #         #then, theorize best way to acquire data over interval
#     #         #let it run and just acquire 100 curvestream?

#     #         acqCounter = 0

#     #         #while acqCounter < 100:                    
                    
                   
#         #increments freq up by stepSize
#         # valonController.valonStepUp()
#         # zaberController.homeZaber()
#         # valonCounter+=1



def main():
    global valonConnect

    #initialize devices: osc, srs, valon, zaber
    oscilloscopeController.initializeScope()
    #oscilloscopeController.estabOscFFTSettings()
    #oscilloscopeController.grabParam()
    SRScontroller.initializeSRS()
    valonConnect = valonController.initializeValon('COM3')
    valonController.valonSettings()
    zaberController.initializeZaber()
    calibrationInit()
    calibrateRun()

    #getting current mode: 'Waveform/PCFFT', 'FFTWF', 'ContWF', 'ContFFT'
    #modeSetting = oscilloscopeController.mode()
    # print(modeSetting)
    
    # match modeSetting['mode']:
    #     case 'Waveform/PCFFT':
    #         waveformPCFFT()
    #     case 'FFTWF':
    #         fftFromScope()
        
    

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

#problems and possible solns:
#have to run two acquisitions and then only the second plots right... could be grabParam() prior to scopeSettings being set? 
#max wont change faster than the frequency ***********

