import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import matplotlib.pyplot as plt # http://matplotlib.org/
import numpy as np # http://www.numpy.org/
from scipy.fft import fft, fftfreq #fourier operations

def run():
    global record, tscale, tstart, bin_wave, vpos, vscale, voff, scale, rate
    visa_address = 'TCPIP0::169.254.23.223::inst0::INSTR'
    print("Connecting to ", visa_address, "...")

    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
    scope.timeout = 10000 # ms
    scope.encoding = 'latin_1'
    scope.read_termination = '\n'
    scope.write_termination = '\n'
    scope.write('*cls') # clear ESR

    print(scope.query('*idn?'))

    input("""
    ACTION:
    Connect probe to oscilloscope Channel 1 and the probe compensation signal.

    Press Enter to continue...
    """)

    dataMode = int(input("""Set data mode:
          "1": RAW
          "2": Avg()
          "3": Fourier Transformed
          """))

    scope.write('*rst') # reset
    t1 = time.perf_counter()
    r = scope.query('*opc?') # sync
    t2 = time.perf_counter()
    print('reset time: {}'.format(t2 - t1))

    scope.write('autoset EXECUTE') # autoset
    t3 = time.perf_counter()
    r = scope.query('*opc?') # sync
    t4 = time.perf_counter()
    print('autoset time: {} s'.format(t4 - t3))

    # io config
    scope.write('horizontal:mode:scale 200E-9')
    scope.write('header 0')
    scope.write('data:encdg SRIBINARY')
    scope.write('data:source CH1') # channel
    scope.write('data:start 1') # first sample
    record = int(scope.query('horizontal:recordlength?'))
    scope.write('data:stop {}'.format(record)) # last sample
    scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

    print("Record Length: ", record)

    # acq config
    scope.write('horizontal:mode:scale 200E-9')
    scope.write('acquire:state OFF') # stop
    #mvVals
    scale = float(scope.query('horizontal:mode:scale?'))
    rate = float(scope.query('HORizontal:DIGital:SAMPLERate?'))
    #scope.write('HORIZONTAL:MODE:RECORDLENGTH 1000')
    scope.write('select:ch1 on')
    scope.write('acquire:mode sample')
    scope.write('acquire:stopafter SEQUENCE') # single
    
    if dataMode == 2:
        print("Data Mode: AVG(CH1)")
        scope.write('MATH1:DEFINE AVG(CH1)')
    elif dataMode == 3:
        print("Data Mode: Fourier Transform")
        scope.write('MATH1:DEFINE AVG(CH1)')
        scope.write('MATH2:DEFINE SpectraMag(Math1)')


    print(scope.query('BUSY?'))
    scope.write('acquire:state ON') # run
    print(scope.query('BUSY?'))
    t5 = time.perf_counter()
    #r = scope.query('*opc?') # sync
    t6 = time.perf_counter()
    print('acquire time: {} s'.format(t6 - t5))

    # data query
    t7 = time.perf_counter()
    bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
    t8 = time.perf_counter()
    print('transfer time: {} s'.format(t8 - t7))

    # retrieve scaling factors
    tscale = float(scope.query('wfmoutpre:xincr?'))
    print(tscale)
    tstart = float(scope.query('wfmoutpre:xzero?'))
    vscale = float(scope.query('wfmoutpre:ymult?')) # volts / level
    voff = float(scope.query('wfmoutpre:yzero?')) # reference voltage
    vpos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)

    # error checking
    r = int(scope.query('*esr?'))
    print('event status register: 0b{:08b}'.format(r))
    r = scope.query('allev?').strip()
    print('all event messages: {}'.format(r))

    scope.close()
    rm.close()

#https://realpython.com/python-scipy-fft/#why-would-you-need-the-fourier-transform
#file:///C:/Users/GRU%20LAB/Downloads/manual.pdf

def plotMath():
    global scaled_wave
    # create scaled vectors
    # horizontal (time)
    total_time = tscale * record
    tstop = tstart + total_time
    scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
    # vertical (voltage)
    unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
    scaled_wave = (unscaled_wave - vpos) * vscale + voff



    print(rate)
    print(scale)
    normalizer = int(rate*scale)
    print(normalizer)
    #fourier transform
    fourier_wave = fft(scaled_wave)
    fourier_time =  fftfreq(normalizer, 1/record)

    print(scaled_wave)
    print(max(scaled_wave))
    print(min(scaled_wave))
    print(fourier_wave)
    # plotting
    plt.plot(scaled_time, scaled_wave)
    plt.title('channel 1') # plot label
    plt.xlabel('time (seconds)') # x label
    plt.ylabel('voltage (volts)') # y label
    print("look for plot window...")
    plt.show()

    plt.plot(fourier_time, np.abs(fourier_wave))
    plt.title('channel 1') # plot label
    plt.xlabel('time (seconds)') # x label
    plt.ylabel('voltage (volts)') # y label
    print("look for plot window...")
    plt.show()



def writeToTxt():
    file = open("dataWave.txt", "w+")
    content = str(scaled_wave)
    file.write(content)
    file.close()

run()
plotMath()
writeToTxt()