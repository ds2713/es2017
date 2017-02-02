from machine import Pin, I2C
import ads1x15
import time
import math
import network
from umqtt.simple import MQTTClient

def main():

	# Connect to network, then wait
	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	sta_if.connect('EEERover', 'exhibition')
	time.sleep(5)

	# Confirming network connection successful
	print(sta_if.ifconfig())

	# FTP Server
    import uftpd

	# Initial MQTTClient
	CLIENT_ID = 'mdma'
	CLIENT_TOPIC = '/esys/mdma'
	client = MQTTClient(CLIENT_ID, '192.168.0.10')
	client.connect()
	# Send MQTT Message at boot to confirm success
	client.publish(CLIENT_TOPIC, bytes('MDMA live', 'utf-8'))

	# Setup i2c class for interface with ADC
	i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
	i2cAddress = i2c.scan()
	numBytes = 1
	# ADC configuration
	ads = ads1x15.ADS1115(i2c, address=72)

	# Initialise parameters for measurements
	samples = 100
	history = 25
	future = samples - history - 1
	threshold = 50

	# Initialise registers and pointers
	output_reg = [0]*samples
	historic_reg = [0]*history
	reading_pointer = 0
	hist_pointer = 0

	# Infinite reading loop
	while True:

		reading = ads.read(0)

		if math.fabs(reading) > threshold:

			# Copy history into output register
			# for x in range (0, history):
			# 	output_reg[x] = historic_reg[(hist_pointer+1)%history]
			# 	hist_pointer = (hist_pointer+1)%history

			# Add current reading to output register
			output_reg[history+1] = reading;

			# Fill output register with up-to-date readings
			for future_pointer in range (0,future):
				output_reg[future_pointer+history+1] = ads.read(0)

			# Copy history into output register
			output_reg[0:history - hist_pointer] = historic_reg[hist_pointer:history]
			output_reg[history - hist_pointer: history] = historic_reg[0:hist_pointer]

			# For debugging, print output register to terminal
			print('New measurement: ', output_reg)

			# Acquire maximum reading in output register
			maximum_value = max(output_reg)
			output_str = str('Max reading:', maximum_value)
			# Send to broker
			client.publish(CLIENT_TOPIC, bytes(output_str, 'utf-8'))

		else:
			# Implementation of circular buffer for historical readings
			historic_reg[hist_pointer] = reading
			hist_pointer = (hist_pointer+1)%history

if __name__ == "__main__":
    # execute only if run as a script



    main()

# except:
# 	print('Stopped')
