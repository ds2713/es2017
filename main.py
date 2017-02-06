from machine import Pin, I2C
import ads1x15
import time
import math
import network
import machine
import json
from umqtt.simple import MQTTClient

# Repeated use of network connnection
def connect_network():
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

# Main function
def main():
	# Connect to network, then wait
	connect_network()

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

	# Setup LED (active low) and buzzer (active high)
	# LED for processing time, buzzer for noting shocks.
	led = Pin(2, Pin.OUT)
	led.high()
	buzzer = Pin(0, Pin.OUT)
	buzzer.low()

	# Time setup. Future network setup.
	# Year, Month, Day, Weekday, Hour, Minutes, Seconds, Milliseconds
	time_tuple = (2017, 1, 1, 0, 12, 00, 10, 0)
	rtc = machine.RTC()
	rtc.datetime(time_tuple)

	# Initialise parameters for measurements
	samples = 100
	history = 25
	future = samples - history - 1
	threshold = 50

	# Initialise registers and pointer
	output_reg = [0]*samples
	historic_reg = [0]*history
	hist_pointer = 0
	index = 0

	# Message cache (not quite heap) initialise
	message_cache = []

	print("Begin reading values.")
	# Infinite reading loop
	while True:

		reading = ads.read(0)

		if math.fabs(reading) > threshold:
			# Capture time
			shock_time = time.localtime()

			# Turn on cues, visual, audio.
			buzzer.high()
			led.low()

			# Add current reading to output register
			output_reg[history+1] = reading;

			# Fill output register with up-to-date readings
			for future_pointer in range (0,future):
				output_reg[future_pointer+history+1] = ads.read(0)

			# Turn buzzer off
			buzzer.low()

			# Copy history into output register
			output_reg[0:history - hist_pointer] = historic_reg[hist_pointer:history]
			output_reg[history - hist_pointer: history] = historic_reg[0:hist_pointer]

			# Acquire reading statistics for output register
			maximum_value = max(output_reg)
			mean_value = float(sum(output_reg))/float(len(output_reg))

			# Construct JSON
			message = {
				'index' : index,
				'time' : shock_time,
				'max_value' : maximum_value,
				'mean_value' : mean_value
			}

			output_str = json.dumps(message)

			# Send to broker, catch sending errors
			try:
				# If cache is not empty, send oldest to newest messages
				# Then delete message, repeat until empty
				while len(message_cache) > 0:
					client.connect()
					client.publish(CLIENT_TOPIC, bytes(message_cache[0], 'utf-8'))
					del message_cache[0]

				# Send current message
				client.connect()
				client.publish(CLIENT_TOPIC, bytes(message_cache[0], 'utf-8'))

			except:
				message_cache.append(output_str)

			# Reinitialise historic_reg and pointer
			# Because it contains outdated info.
			historic_reg = [0]*history
			hist_pointer = 0
			# Turn off LED and update index
			led.high()
			index = index + 1

		else:
			# Implementation of circular buffer for historical readings
			historic_reg[hist_pointer] = reading
			hist_pointer = (hist_pointer+1)%history

if __name__ == "__main__":
	main()
