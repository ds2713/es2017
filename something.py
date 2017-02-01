from machine import Pin, I2C
import ads1x15
import time

i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
i2cAddress = i2c.scan()
numBytes = 1

samples = 100
history = 10
future = samples - history - 1
threshold = 20

ads = ads1x15.ADS1115(i2c, address=72)

value = [0]*samples
historic_reading = [0]*history
reading_pointer = 0
hist_pointer = 0

while True:

	reading = ads.read(0)

	if reading > threshold:

		for x in range (0, history):
			value[x] = historic_reading[(hist_pointer+1)%history]
			hist_pointer = (hist_pointer+1)%history

		value[history+1] = reading;

		for future_pointer in range (history+1,future):
			value[future_pointer] = ads.read(0)

		print(value)

	else:

		historic_reading[hist_pointer] = reading
		hist_pointer = (hist_pointer+1)%history
