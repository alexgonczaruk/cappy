import RPi.GPIO as GPIO
import sys, termios, time, tty

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
keyInput = 0

def init():
    # White = Reverse
    # Blue = Stop

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(32, GPIO.OUT) # IO 12 = PWM Left
    GPIO.setup(38, GPIO.OUT) # IO 20 = Reverse Left
    GPIO.setup(40, GPIO.OUT) # IO 21 = Break Left

    GPIO.setup(33, GPIO.OUT) # IO 13 = PWM Right
    GPIO.setup(16, GPIO.OUT) # IO 23 = Right Reverse
    GPIO.setup(37, GPIO.OUT) # IO 26 = Break Right

    # LEFT
    GPIO.output(38, False)

    #RIGHT
    GPIO.output(16, False)

    # Break
    GPIO.output(40, False)
    GPIO.output(37, False)

def brake(tf): 
    GPIO.output(40, True)
    GPIO.output(37, True)
    time.sleep(tf)


def forward(tf): 
    # Brake -> False
    GPIO.output(40, False)
    GPIO.output(37, False)

    GPIO.output(38, True)
    motorl = GPIO.PWM(32, 30) # 20000 is max, 26 is tipping point
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(16, False)
    motorr = GPIO.PWM(33, 30)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def reverse(tf):
    # Brake -> False
    GPIO.output(40, False)
    GPIO.output(37, False)

    GPIO.output(38, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(16, True)
    motorr = GPIO.PWM(33, 50) # when this was 50, it was going faster
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def left(tf):
    # Brake -> False
    GPIO.output(40, False)
    GPIO.output(37, False)

    GPIO.output(38, True)
    motorl = GPIO.PWM(32, 35) #20 000 is max, 25 IS TIpping point
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    time.sleep(tf)

def right(tf): 
    # Brake -> False
    GPIO.output(40, False)
    GPIO.output(37, False)

    GPIO.output(16, False)
    motorr = GPIO.PWM(33, 35)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

init()

while True:
    keyInput = sys.stdin.read(1)[0]
    print("Input:", keyInput)

    sleep_time = 0.01

    if keyInput == 'w':
        forward(sleep_time)
    elif keyInput == 's':
        reverse(sleep_time)
    elif keyInput == 'a':
        left(sleep_time)
    elif keyInput == 'd':
        right(sleep_time)
    elif keyInput == 'b':
        brake(sleep_time)
    elif keyInput == 'k':
        GPIO.output(15, False)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)