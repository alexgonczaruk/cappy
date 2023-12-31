import RPi.GPIO as GPIO
import sys, termios, time, tty

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
keyInput = 0

# 32 = the motor PWM connection
# 31 = be stop
# 29 = the reverse connection

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(29, GPIO.OUT)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(32, GPIO.OUT)

def forward(tf): 
    GPIO.output(29, False)
    GPIO.output(31, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(20)
    time.sleep(tf)

def reverse(tf): 
    GPIO.output(29, True)
    GPIO.output(31, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(20)
    time.sleep(tf)

def brake(tf): 
    GPIO.output(31, True)
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
