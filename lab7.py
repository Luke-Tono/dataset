from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
import RPi.GPIO as GPIO
import time
import sys

# Configure PubNub
pnconf = PNConfiguration()
pnconf.publish_key = 'pub-c-cc09a5e0-ae7e-4f0b-91ba-3c06deac8056'
pnconf.subscribe_key = 'sub-c-600de055-e08b-4dfd-8f69-231ee45b2313'
pnconf.uuid = 'z728'
pubnub = PubNub(pnconf)
channel = 'zhaox207'

# Setup GPIO
GPIO.setmode(GPIO.BCM)
TRIG = 20
ECHO = 26
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Publish callback function
def publish_callback(result, status):
    if status.is_error():
        print(f"Publish error: {status.category}, {status.error_data}")
    else:
        print(f"Published successfully with timetoken: {result.timetoken}")

print("Distance measurement in progress")
GPIO.output(TRIG, False)
print("Waiting for sensor to settle")
time.sleep(2)

try:
    while True:
        # Trigger ultrasonic pulse
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        print("Before pulse start")
        
        # Measure time
        pulse_start = time.time()
        timeout_start = time.time()
        
        # Add timeout to prevent infinite loop
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if time.time() - timeout_start > 1:  # 1 second timeout
                raise Exception("Sensor timeout waiting for echo start")
                
        timeout_start = time.time()
        pulse_end = pulse_start
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if time.time() - timeout_start > 1:  # 1 second timeout
                raise Exception("Sensor timeout waiting for echo end")
                
        print("After pulse")
        
        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        print(f"Distance: {distance} cm")
        
        # Correct publish method
        message = {'distance': distance}
        pubnub.publish().channel(channel).message(message).async(publish_callback)
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Measurement stopped by user")
except Exception as e:
    print(f"Error: {e}")
finally:
    GPIO.cleanup()
    sys.exit()
