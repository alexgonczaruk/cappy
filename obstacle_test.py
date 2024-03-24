import random, serial, socket, sys, termios, time, tty
import adafruit_gps, py_qmc5883l
import RPi.GPIO as GPIO

from math import cos, asin, sqrt, pi, radians, atan2, degrees
from time import sleep
from test_obstacle_detection import detection

# sensor = py_qm/c5883l.QMC5883L()
# sensor.declination = 9.46
# sensor.calibration = [[1.0800920732995762, 0.1737669228645332, 858.6715020334207], [0.1737669228645332, 1.3770028947667214, -884.0944994333294], [0.0, 0.0, 1.0]]
# sensor.calibration = [[ 1.08802835, -0.0763318563, -409.867226], [-0.0763318563,  1.06618950, -394.741495], [ 0.00000000, 0.00000000, 1.00000000]]

serverIP = "192.168.2.36" # Shehan's hotspot
serverPORT = 8888

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverIP, serverPORT))
serverSocket.listen()

print("Waiting for connection")
connectionSocket, addr = serverSocket.accept()
print("connected to client!")

ACTION = "ACTION"
COORDINATE = "COORDINATE"

lat_avg = []
lon_avg = []
last = time.monotonic()
MAX_LIST_SIZE = 3

uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')

GLOBAL_OBSTACLE_STOP = False

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
keyInput = 0

# <--- MOTOR FUNCTIONS -->
def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(22, GPIO.OUT) # GPIO 25
    GPIO.setup(29, GPIO.OUT) # GPIO 5
    GPIO.setup(32, GPIO.OUT) # GPIO 12, PWM
    
    GPIO.setup(33, GPIO.OUT) # GPIO 13, PWM
    GPIO.setup(36, GPIO.OUT) # GPIO 16
    GPIO.setup(37, GPIO.OUT) # GPIO 26
    
    # LEFT
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, False)

    #RIGHT
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, False)

    # Why do we need this twice, can we remove below line?
    GPIO.setup(22, GPIO.OUT)

    # Break
    GPIO.output(22, False)
    GPIO.output(37, False)

    # Why do we need this twice, can we remove below line?
    GPIO.output(22, False)

def brake(tf): 
    GPIO.output(22, True)
    GPIO.output(37, True)
    # time.sleep(tf)


def forward(tf):
    # Brake -> False
    GPIO.output(22, False)
    GPIO.output(37, False)

    GPIO.output(16, True)
    motorl = GPIO.PWM(32, 30) #20 000 is max, 26 is tipping point
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, False)
    motorr = GPIO.PWM(33, 30)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    # time.sleep(tf)

def reverse(tf):
    # Brake -> False
    GPIO.output(22, False)
    GPIO.output(37, False)

    GPIO.output(16, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, True)
    motorr = GPIO.PWM(33, 50) # when this was 50, it was going faster
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def left(scaling_factor):
    # Brake -> False
    GPIO.output(22, False)
    GPIO.output(37, False)

    GPIO.output(16, True)
    motorl = GPIO.PWM(32, 35)
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, False)
    motorr = GPIO.PWM(33, (35 + scaling_factor))
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    # time.sleep(tf)

def right(scaling_factor): 
    # Brake -> False
    GPIO.output(22, False)
    GPIO.output(37, False)

    GPIO.output(16, True)
    motorl = GPIO.PWM(32, (35 + scaling_factor))
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, False)
    motorr = GPIO.PWM(33, 35)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    # time.sleep(tf)

# def get_compass_bearing(direction_to_turn):
#     angle = sensor.get_bearing()        
#     print('Heading Angle = {}°'.format(angle))
#     # diff = angle - ((direction_to_turn + 360) % 360)
#     diff = 0
#     # if direction_to_turn > 0:
#     #     diff = (angle + direction_to_turn) % 360
#     #     print(f"angle [{angle}] + direction_to_turn {direction_to_turn}  % 360 = {diff}")

#     # else:
#     #     diff = (angle - direction_to_turn) % 360
#     #     print(f"angle [{angle}] - direction_to_turn {direction_to_turn}  % 360 = {diff}")

#     diff = (direction_to_turn - angle)
#     print(f"direction_to_turn [{direction_to_turn}] - angle [{angle}] = {diff}")

#     return diff

def get_rpi_coordinates(last = time.monotonic()):
    gps.update()

    current = time.monotonic()
    if current - last >= 1.0:
        last = current
        if not gps.has_fix:
            print(f"gps does not have fix so printing {0}, {0}, {last}, {lat_avg}, {lon_avg}")
            return 43.4766059, -80.5383448, last

    lat = gps.latitude if gps.latitude is not None else 0
    lon = gps.longitude if gps.longitude is not None else 0
    return lat, lon, last

# for latitude, if the diff lat2>lat1, the phone is more north. Move north
# for longitude, if the diff lon2>lon1, the phone is more east. Move east
def distance(lat1, lon1, lat2, lon2):
    r = 6371000 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2

    dist = 2 * r * asin(sqrt(a))

    return dist

def calculate_angle_offset(lat1, lon1, lat2, lon2):
    # Convert latitudes and longitudes to radians
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Calculate the angle offset (bearing) using simplified tangent approximation
    angle_offset = atan2(lon2_rad - lon1_rad, lat2_rad - lat1_rad)

    # Convert angle offset from radians to degrees
    angle_offset_deg = degrees(angle_offset)
    direction = "NW"
    if lat2>lat1:
        if lon2>lon1:
            direction = "NE"
    else:
        if lon2>lon1:
            direction = "SE"
        else:
            direction = "SW"

    return angle_offset_deg, direction

def parse_location(content):

    # Parse the phone's coordinates
    try:
        phone_location = content.split(", ")
        phone_location_lat = float(phone_location[0])
        phone_location_lon = float(phone_location[1])

        print(f"Coordinates: {phone_location_lat}, {phone_location_lon}")

        return phone_location_lat, phone_location_lon
    except:
        return 0, 0

message = ""
code = ""
content = ""
waitToinitialize = 0
connectionSocket.setblocking(False)

sleep_time = 0.01
init()

NotFirstTime = False

pi_location_lat = 0
pi_location_lon = 0

phone_location_lat = 0
phone_location_lon = 0
distance_from_phone = 1000
distance_from_phone_str = "PI:1000"

def motors_forward(power_left, power_right):
    GPIO.output(22, False)
    GPIO.output(37, False)

    GPIO.output(16, True)
    motorl = GPIO.PWM(32, power_left)
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, False)
    motorr = GPIO.PWM(33, power_right)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)
    time.sleep(0.5)

while True:

    # make socket non-blocking, ensure we receive first 3 messages before continuing
    try:
        while waitToinitialize < 3 or NotFirstTime:
            message = connectionSocket.recv(1024).decode()
            print(f"Raw content: {message}")
            code, content = message.split(":", 1)

            print(f"Incoming action: {content}")
            if not NotFirstTime:
                connectionSocket.send("SETUP:SETUP".encode())

            waitToinitialize = waitToinitialize + 1
            NotFirstTime = True

    except socket.error as e:
        print("passing")
        time.sleep(0.1)

        # obstacle detection
        obstacle_distance, strength = detection()

        # pre-screening, may need to adjust strength threshold
        if obstacle_distance >= 0.2 and obstacle_distance <= 2 and strength >= 900:
            brake(sleep_time)
            print("Motors: Brake")

            while True:
                connectionSocket.send("ACTION:STOP".encode())
                time.sleep(0.1)
            GLOBAL_OBSTACLE_STOP = True
            continue

       
        print(f"LAST PRINT: Pi's distance from phone: {distance_from_phone_str}")
        print("="*100)
        test = 5
        connectionSocket.send("PI:5".encode())
        