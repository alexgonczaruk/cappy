import RPi.GPIO as GPIO
import sys, termios, time, tty

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
keyInput = 0

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(29, GPIO.OUT) # GPIO 5
    GPIO.setup(22, GPIO.OUT) # GPIO 25
    GPIO.setup(32, GPIO.OUT) # GPIO 12, PWM
    
    GPIO.setup(33, GPIO.OUT) # GPIO 13, PWM
    GPIO.setup(36, GPIO.OUT) # GPIO 16
    GPIO.setup(37, GPIO.OUT) # GPIO 26
    
    # LEFT
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, False)
    # GPIO.setup(36, GPIO.OUT)
    # GPIO.output(36, False)

    #RIGHT
    GPIO.setup(36, GPIO.OUT)
    GPIO.output(36, False)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, False)

    GPIO.output(37, False)
    GPIO.output(22, False)

def brake(tf): 
    GPIO.output(22, True)
    GPIO.output(37, True)
    time.sleep(tf)


def forward(tf): 
    # GPIO.output(22, True)
    GPIO.output(22, False)
    GPIO.output(37, False)
    GPIO.output(16, True)
    motorl = GPIO.PWM(32, 30) #20 000 is max, 26 IS TIpping point
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    # GPIO.output(37, False)
    GPIO.output(36, False)
    motorr = GPIO.PWM(33, 30)
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def reverse(tf): 
    GPIO.output(16, False)
    # GPIO.output(22, False)
    motorl = GPIO.PWM(32, 50)
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    GPIO.output(36, True)
    # GPIO.output(37, True)
    motorr = GPIO.PWM(33, 50) # when this was 50, it was going faster
    motorr.start(0)
    motorr.ChangeDutyCycle(100)

    time.sleep(tf)

def left(tf): 
    # GPIO.output(22, True)
    GPIO.output(16, True)
    motorl = GPIO.PWM(32, 35) #20 000 is max, 25 IS TIpping point
    motorl.start(0)
    motorl.ChangeDutyCycle(100)

    time.sleep(tf)

def right(tf): 
    # GPIO.output(37, False)
    GPIO.output(36, False)
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