# import gy271compass as GY271
# from time import sleep

# sensor = GY271.compass(address=0x0d)

# print('[Press CTRL + C to end the script!]')
# try:
#     while True:
#         angle = sensor.get_bearing()       
#         temp = sensor.read_temp()
    
#         print('Heading Angle = {}°'.format(angle))
#         print('Temperature = {:.1f}°C'.format(temp))
#         sleep(2)

# except KeyboardInterrupt:
#     print('\nScript end!')

# git clone https://github.com/RigacciOrg/py-qmc5883l.git to use import
import py_qmc5883l
from time import sleep

sensor = py_qmc5883l.QMC5883L()
sensor.declination = 9.46
sensor.calibration = [[1.6330085087384014, 0.0323886463392132, 1763.0899153395242], [0.032388646339213206, 1.0016572042827312, 2448.0388464736657], [0.0, 0.0, 1.0]]

print('[Press CTRL + C to end the script!]')
try:
    while True:
        angle = sensor.get_bearing()       
        print('Heading Angle = {}°'.format(angle))
        sleep(2)

except KeyboardInterrupt:
    print('\nScript end!')