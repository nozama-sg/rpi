import RPi.GPIO as GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BOARD)
GPIO.setup([18,7], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    if GPIO.input(18) == GPIO.HIGH:
        print("Button WHITE pushed")

    if GPIO.input(7) == GPIO.HIGH:
        print("Button BLACK was pushed!")
