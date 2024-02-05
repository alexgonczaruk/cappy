import RPi.GPIO as GPIO
import sys, termios, time, tty

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
keyInput = 0

# 32 = the motor PWM connection, GPIO 12
# 31 = be stop, GPIO 6 ----- now using pin 22, GPIO 25
# 29 = the reverse connection, GPIO 5
# new stop is io 6, old stop is io 25, reverse is 5

# 33 - motor PWM connection, GPIO 13
# 36 - be stop, GPIO 16 ------ GPIO 24 , pin 18
# 37 - reverse connection, GPIO 26
# io 23, pin 16
# reverse is io 26, old stop is io 16, new stop is io 23 pin 16 (1 motor)


def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(29, GPIO.OUT) # GPIO 5
    GPIO.setup(22, GPIO.OUT) # GPIO 6
    GPIO.setup(32, GPIO.OUT) # GPIO 12, PWM
    
    GPIO.setup(33, GPIO.OUT) # GPIO 13, PWM
    GPIO.setup(36, GPIO.OUT) # GPIO 16
    GPIO.setup(37, GPIO.OUT) # GPIO 26

    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, False)
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, False)

    GPIO.setup(31, GPIO.OUT)
    GPIO.output(31, False)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, False)

def forward(tf): 
    # GPIO.output(22, True)
    GPIO.output(29, False)
    motorl = GPIO.PWM(32, 35) #20 000 is max, 25 IS TIpping point
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(37, True)
    # GPIO.output(36, False)
    motorr = GPIO.PWM(33, 35)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def reverse(tf): 
    GPIO.output(29, True)
    GPIO.output(22, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, False)
    GPIO.output(37, False)
    motorr = GPIO.PWM(33, 50) # when this was 50, it was going faster
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def brake(tf): 
    GPIO.output(22, True)
    GPIO.output(36, True)
    time.sleep(tf)


def OldOff():
    # 22, 36
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, False)
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, False)

def OldOn():
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, True)
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, True)

def NewOff():
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, False)
    GPIO.setup(31, GPIO.OUT)
    GPIO.output(31, False)

def NewOn():
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, True)
    GPIO.setup(31, GPIO.OUT)
    GPIO.output(31, True)

def toggleNo():
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, False)
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, False)

    GPIO.setup(31, GPIO.OUT)
    GPIO.output(31, False)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, False)

def toggleYes():
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, True)
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, True)

    GPIO.setup(31, GPIO.OUT)
    GPIO.output(31, True)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, True)

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
    elif keyInput == 'o':
        OldOff()
    elif keyInput == 'p':
        OldOn() # THIS STOPS ON A DOT
    elif keyInput == '[':
        NewOff()
    elif keyInput == ']':
        NewOn() # BLASTS THE SPEED

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
