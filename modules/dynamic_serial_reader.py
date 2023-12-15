"""
more or less the same as the serial read to store a file (csv)

this reader store data directly into a pandas dataframe for live update a graph

"""
import sys
import glob
import serial
import time 

from threading import Thread
from tasks import *

import pandas as pd

ser = None

def createSerialObject(port, baud=115200, tout=5):
    global ser
    try:
        ser = serial.Serial(port=port, baudrate=baud, timeout=tout)
    except IOError as err:
        return None

    return ser 
   
def readSerialData(df:pd.DataFrame, port):
    global ser
    if port is not None:
        if ser is None:
            ser = createSerialObject(port)
            if ser is None:
                return df
        # read serial
        line = ser.readline()
        try:
            l = line.decode('utf-8').splitlines()
            #print (l)
        except UnicodeDecodeError as err:
            return df
        if (len(l) > 0):
            raw = l[0].split(',')
            if raw[0] != "FEEF":
                return df
        else:
            return df
        #
        # and next row to dataframe, ignore first byte (sync byte FEEF)
        print(raw[1:])   
        df.loc[len(df)] = raw[1:]
    return df
        
def scanSerialPorts():
    """ Lists serial port names
        => StackOverflow: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    ports = []
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def testSerialPort(port:serial.Serial) -> bool:
    if port is None:
        return False
    try:
        checks = 0
        while checks < 3:
            port.close()
            time.sleep(0.5)
            port.open()
            time.sleep(0.5)
            checks += 1            

        port.close()
    except (OSError, serial.SerialException) as err:
        print (err)
        return False
    return True

