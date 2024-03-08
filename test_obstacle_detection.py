import serial,time
import numpy as np

def read_tfluna():
    ser = serial.Serial("/dev/ttyUSB0", 115200,timeout=0) # mini UART serial device
    if ser.isOpen() == False:
        ser.open() # open serial port if not open

    while True:
        counter = ser.in_waiting # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9) # read 9 bytes
            ser.reset_input_buffer() # reset buffer

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59: # check first two bytes
                distance = bytes_serial[2] + bytes_serial[3]*256 # distance in next two bytes
                strength = bytes_serial[4] + bytes_serial[5]*256 # signal strength in next two bytes
                temperature = bytes_serial[6] + bytes_serial[7]*256 # temp in next two bytes
                temperature = (temperature/8.0) - 256.0 # temp scaling and offset
                return distance/100.0,strength,temperature

def detection():
    if ser.isOpen() == False:
        ser.open() # open serial port if not open

    avg_dist = 0
    avg_strength = 0
    WINDOW = 3

    for _ in range(WINDOW):
        distance,strength,_ = read_tfluna() # read values
        avg_dist += distance
        avg_strength += strength
    
    avg_dist /= WINDOW
    avg_strength /= WINDOW


    print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit)'.\
              format(avg_dist,avg_strength)) # print sample data
    
    return avg_dist, avg_strength

# ser = serial.Serial("/dev/serial0", 115200,timeout=0) # mini UART serial device
# if ser.isOpen() == False:
#    ser.open() # open serial port if not open

# detection()
# ser.close() # close serial port