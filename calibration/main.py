import time
import pyvisa as visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import valonController, oscilloscopeController, zaberController, SRScontroller

#initializing calibration variables, commands, devices, etc.
def calibrationInit():
    global valonFreq, valonFreqStep, stepUpVar, startPosZaber, endPosZaber, speedZaber, trigFreq, moveVelMM, endDistZaberMM, startPosZaberMM, awgFreq

    awgFreq = float(input("What is the AWG frequency? (EX: 30 if 30mHz): "))
    oscilloscopeController.estabMAXSettings(awgFreq)
    #Valon config
    totalFreq = float(input("Starting TOTAL (AWG INCLUDED, THIS SUBTRACTS IT FOR YOU) frequency? (MHz): "))
    valonFreq = totalFreq - awgFreq
    valonController.writeValonCommand(f"Frequency {valonFreq} M")

    #getting freq step if needed
    print("******IF ONLY RUNNING ONCE, ENTER ANYTHING BUT A NUMBER")
    valonFreqStep = input("Freq step size? (MHz): ")
    
    try:
        valonFreqStep = float(valonFreqStep)
        stepUpVar = True
    except ValueError:
        stepUpVar = False
        print("Only running single sequence.")

    #Zaber config
    # setZaber = input("Setup Zaber? Y/N: ")
    # if setZaber == "Y":
    #sends zaber to 0mm     
    #1mm = 20997.375 steps
    #1m/s = 3040.2099738 steps/s

    #setting zaber travel dist, initial start pos:
    while True: 
        try:
            #OLD, FIX ME
            startPosZaber = float(input("Starting position? (mm): "))
            endPosZaber = float(input("Ending position? (mm): "))
            
            #FIX ME *****************************************************************************************************************************
            #startPosZaber = ((4.23491632201815e-9*(totalFreq**2)) + (0.00214275759953761*totalFreq) - 2.05776365002228)
            #double for this since the first val taken out of midpt
            totalDist = endPosZaber - startPosZaber

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

    #speed for zaber
    while True:
        try:
            speedZaber = float(input("Set the movement velocity of the Zaber (mm/s, max 3.5m/s): "))
            moveVelMM = speedZaber
            if speedZaber <= 3.5 and speedZaber > 0:
                totalTime = totalDist/speedZaber
                print("Run time is: ", totalTime)
                speedZaber = round(speedZaber * 34402.099737532773)
            elif speedZaber < 0 or speedZaber > 3.5:
                raise ValueError
            break
        except ValueError:
            print("Invalid integer. The number must be between 0 and 3.5mm.")

    totalTime = totalDist/speedZaber

    zaberController.zaberSetup(startPosZaber, endPosZaber)

    #SRS config
    trigFreq = SRScontroller.setFreq()



#start by triggering, runs zaber totality of 
def calibrateRun():
    global maxList, timeList
    maxList = []
    timeList = []
    maxMaxVals = []


    #set max speed back to fast or this will be SLOW on SLOW MOVES
    zaberController.zaberSetSpeed(101204)
    startZaber = startPosZaber/20997
    print(f"Moving Zaber to {startZaber}.")
    zaberController.moveToZaber(startPosZaber)
    zaberController.zaberDevice.poll_until_idle()
    currPos = zaberController.zaberDevice.get_position()
    print("Homing... Zaber is at position: ", currPos/20997)
    zaberController.zaberDevice.poll_until_idle()
    zaberController.zaberSetSpeed(speedZaber)

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
        print("Length of max: ", len(maxList))
        print("Length of pos: ", len(posArr))
        print(max(maxLists))
        plt.plot(posArr, maxLists)
        plt.xlabel('Zaber Position (mm)')
        plt.ylabel('Intensity (Volts)')
        plt.show()
        print(max(maxLists))

    for items in maxList:
        print("len: ", len(items))
        maxer = max(items)
        for index, values in enumerate(items):
            if values == maxer:
                print("Max position found: ", posArr[index])
                peakMax = posArr[index]
                maxMaxVals.append(peakMax)
    
    peakMidpt = round((len(maxMaxVals))/2)
    maxPos = maxMaxVals[peakMidpt]

    #moving to max peak pos
    print("Moving to maximum at: ", maxPos, " mm")
    zaberController.zaberSetSpeed(101204)
    zaberController.moveToZaber(int(maxPos*20997))
    zaberController.zaberDevice.poll_until_idle()
    currPos = zaberController.zaberDevice.get_position()
    print("Running scan... Zaber is at position: ", currPos/20997)
    SRScontroller.stopTrig()

    #running experiment
    SRScontroller.startPulse()
    SRScontroller.setTrig(5)

    #acquiring waveform data
    fftFromScope(awgFreq)

    # SRScontroller.stopTrig()
    # SRScontroller.stopPulse()

    #runs next step up if necessary 
    if stepUpVar == True:
        runBool = input("Do you want to run another experiment? (Y/N): ").lower()
        if runBool == "y":
            valonController.valonStepUp()
            calibrateRun()
        else:
            return
        

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
        tempMaxList.append(float(oscilloscopeController.queryOscCmd('MEASUrement:MEAS1:VALUE?')))
    
    maxList.append(tempMaxList)


def fftFromScope(awgFreq):
    timeScale, timeStart, verticalScale, verticalOffset, verticalPosition = oscilloscopeController.grabParam()

    #acquire waveform
    waveValues = oscilloscopeController.acquireFFTDataAtMax(awgFreq)
    
    #stopping experiment
    oscilloscopeController.oscCalibStop()
    SRScontroller.stopTrig()
    SRScontroller.stopPulse()

    #acquire vals
    xValues, yValues = scaleFFT(waveValues, timeStart, timeScale)
    
    #plot values 
    generatePlot(xValues, yValues)

    unscaled_wave = np.array(waveValues, dtype='float') 
    DF = pd.DataFrame(unscaled_wave)
    csvWriting = DF.to_csv("output.csv")

def scaleFFT(waveValues, timeStart, timeScale):
    fftYValues = np.array(waveValues, dtype='float')
    fftXValues = np.linspace(timeStart, timeScale*len(waveValues), len(waveValues), endpoint=False)
    return fftXValues, fftYValues

def generatePlot(xWave, yWave):
    plt.plot(xWave, yWave)
    plt.title("Data")
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.show()
    return

def main():
    global valonConnect

    #initialize devices: osc, srs, valon, zaber
    oscilloscopeController.initializeScope()
    SRScontroller.initializeSRS()
    valonConnect = valonController.initializeValon('COM3')
    valonController.valonSettings()
    zaberController.initializeZaber()
    calibrationInit()
    calibrateRun()

#probably write the initializing into a function where you can use "try:"

if __name__ == "__main__":
    main()

#problems and possible solns:
#have to run two acquisitions and then only the second plots right... could be grabParam() prior to scopeSettings being set? 
#max wont change faster than the frequency ***********

