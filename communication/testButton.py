import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(True) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # DO NOT Use physical pin numbering
GPIO.setup([18,7], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    if GPIO.input(18) == GPIO.HIGH:
        print("Button WHITE pushed")

    if GPIO.input(7) == GPIO.HIGH:
        print("Button BLACK was pushed!")
