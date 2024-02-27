from datetime import datetime # std library
import visa # https://pyvisa.readthedocs.org/en/stable/

# Modify the following lines to configure this script for your instrument
#==============================================
visaResourceAddr = 'MSO5204B'
fileSaveLocation = r'C:\Temp\\' # Folder on your PC where to save image
#==============================================

rm = visa.ResourceManager()
scope = rm.open_resource(visaResourceAddr)

print(scope.query('*IDN?'))

scope.write("HARDCopy:PORT FILE;")
scope.write("EXPort:FORMat PNG")

# Set where the file will be saved on the scope's hard drive.  This is not
# where it will be saved on your PC.
scope.write("HARDCopy:FILEName \"C:\\Temp.png\"")

scope.write("HARDCopy STARt")

# Read the image file from the scope's hard drive
scope.write("FILESystem:READFile \"C:\\Temp.png\"")
imgData = scope.read_raw()

# Generate a filename based on the current Date & Time
dt = datetime.now()
fileName = dt.strftime("%Y%m%d_%H%M%S.png")

# Save the transfered image to the hard drive of your PC
imgFile = open(fileSaveLocation + fileName, "wb")
imgFile.write(imgData)
imgFile.close()

# Delete the image file from the scope's hard drive.
scope.write("FILESystem:DELEte \"C:\\Temp.png\"")

scope.close()
rm.close()