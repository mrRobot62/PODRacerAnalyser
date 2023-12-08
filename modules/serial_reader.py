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

task_running = False

def thread_serial_read(df, duration:float=0.1):
    print("alive...")
    time.sleep(duration)


def prepare_serial_task(df, duration:float=0.1):
    global task_running
    if task_running == False:
        thread = Thread(target=thread_serial_read, args=(df, duration))
        thread.daemon = True
        thread.start()
        task_running = True
    
def readSerialData(df, port, serialAktive:bool):

    if serialAktive:
        pass
    else:
        return port, ""
        
    return port, "running"



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