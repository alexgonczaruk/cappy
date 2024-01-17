import RPi.GPIO as GPIO
import sys, termios, time, tty

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
keyInput = 0

# 32 = the motor PWM connection, GPIO 12
# 31 = be stop, GPIO 6
# 29 = the reverse connection, GPIO 5

# 33 - motor PWM connection, GPIO 13
# 36 - be stop, GPIO 16
# 37 - reverse connection, GPIO 26

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(29, GPIO.OUT)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(32, GPIO.OUT)
    
    # GPIO.setup(33, GPIO.OUT)
    # GPIO.setup(36, GPIO.OUT)
    # GPIO.setup(37, GPIO.OUT)

def forward(tf): 
    GPIO.output(29, False)
    GPIO.output(31, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(20)

    # GPIO.output(36, False)
    # GPIO.output(37, False)
    # motorl = GPIO.PWM(33, 50)
    # motorl.start(0)
    # motorl.ChangeDutyCycle(20)

    time.sleep(tf)

def reverse(tf): 
    GPIO.output(29, True)
    GPIO.output(31, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(20)

    # GPIO.output(37, True)
    # GPIO.output(36, False)
    # motorl = GPIO.PWM(33, 50)
    # motorl.start(0)
    # motorl.ChangeDutyCycle(20)

    time.sleep(tf)

def brake(tf): 
    GPIO.output(31, True)
    # GPIO.output(36, True)
    time.sleep(tf)

# Init GPIO
init()

while True:
    keyInput = sys.stdin.read(1)[0]
    print("Input:", keyInput)

    sleep_time = 0.01

    if keyInput == 'w':
        forward(sleep_time)
    elif keyInput == 's':
        reverse(sleep_time)
    elif keyInput == 'b':
        brake(sleep_time)
    elif keyInput == 'k':
        GPIO.output(15, False)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
