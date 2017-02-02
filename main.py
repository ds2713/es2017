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

	# While waiting for a connection, print and wait.
	while sta_if.ifconfig()[0] == '0.0.0.0':
		print("Connecting...")
		time.sleep(0.5)

	# Print successful network IP address.
	print("Network connected. IP Address: " + sta_if.ifconfig()[0])

	# Confirming network connection successful
	# print(sta_if.ifconfig())

	# FTP Server, left out because ampy!
	# import uftpd

	# Initial MQTTClient
	CLIENT_ID = 'mdma'
	CLIENT_TOPIC = '/esys/mdma'
	client = MQTTClient(CLIENT_ID, '192.168.0.10')
	client.connect()
	# Send MQTT Message at boot to confirm success
	client.publish(CLIENT_TOPIC, bytes('MDMA MQTT Live', 'utf-8'))
	print("MQTT client successful.")

	# Setup i2c class for interface with ADC
	i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
	i2cAddress = i2c.scan()
	numBytes = 1
	# ADC configuration
	ads = ads1x15.ADS1115(i2c, address=72)
	print("ADC configured.")

	# Initialise parameters for measurements
	samples = 100
	history = 25
	future = samples - history - 1
	threshold = 50

	# Initialise registers and pointer
	output_reg = [0]*samples
	historic_reg = [0]*history
	hist_pointer = 0

	print("Begin reading values.")
	# Infinite reading loop
	while True:

		reading = ads.read(0)

		if math.fabs(reading) > threshold:

			# Add current reading to output register
			output_reg[history+1] = reading;

			# Fill output register with up-to-date readings
			for future_pointer in range (0,future):
				output_reg[future_pointer+history+1] = ads.read(0)

			# Copy history into output register
			output_reg[0:history - hist_pointer] = historic_reg[hist_pointer:history]
			output_reg[history - hist_pointer: history] = historic_reg[0:hist_pointer]

			# For debugging, print output register to terminal
			print('New measurement:', output_reg)

			# Acquire maximum reading in output register
			maximum_value = max(output_reg)
			output_str = 'Max reading: ' + str(maximum_value)
			# Send to broker
			client.publish(CLIENT_TOPIC, bytes(output_str, 'utf-8'))

			# Reinitialise historic_reg and pointer
			# Because it contains outdated info.
			historic_reg = [0]*history
			hist_pointer = 0

		else:
			# Implementation of circular buffer for historical readings
			historic_reg[hist_pointer] = reading
			hist_pointer = (hist_pointer+1)%history

if __name__ == "__main__":
	main()
