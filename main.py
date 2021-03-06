from machine import Pin, I2C, PWM
import ads1x15
import time
import math
import network
import machine
import json
import socket
from umqtt.simple import MQTTClient

# Function to obtain response via HTML.
def http_get(url, port):
	_, _, host, path = url.split('/', 3)
	addr = socket.getaddrinfo(host, port)[0][-1]
	s = socket.socket()
	s.connect(addr)
	s.send(bytes("GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host), "utf8"))
	fullresponse = []
	while True:
		data = s.recv(100)
		if data:
			fullresponse.append(str(data, "utf8"))
		else:
			break
	s.close()
	return fullresponse

# Function to send message via MQTT
def send_mqtt(the_message):
	# Using global to remove need to initialise new object each time
	global client
	global message_cache
	message_json = json.dumps(the_message)
	CLIENT_TOPIC = '/esys/mdma'
	# Send message to broker, catch sending errors
	try:
		client.connect()
		# If cache is not empty, send oldest to newest messages
		# Then delete message, repeat until empty
		while len(message_cache) > 0:
			client.publish(CLIENT_TOPIC, bytes(message_cache[0], 'utf-8'))
			del message_cache[0]

		# Send current message
		client.publish(CLIENT_TOPIC, bytes(message_json, 'utf-8'))
		# Disconnect each time to prevent timeout which will cause an exception.
		client.disconnect()

	# If cannot send, save to cache.
	except:
		message_cache.append(message_json)

# Main function
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

	# FTP Server, left out because ampy!
	# import uftpd

	# Initial MQTTClient
	CLIENT_ID = 'mdma'
	global client
	client = MQTTClient(CLIENT_ID, '192.168.0.10')
	# Message cache for unsent ones
	global message_cache
	message_cache = []
	# Send MQTT Message at boot to confirm success
	send_mqtt('MDMA MQTT Live!')
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
	buzzer = PWM(Pin(0), freq=500, duty=0)

	# Time setup from network. If not, set to midnight, Jan 1, 2017.
	print("Configuring time from network.")
	try:
		response = http_get("http://192.168.1.118/", 8080)
		response_string = str(response).split("START")[-1].split("END")[0]
	except:
		response_string = '2017,1,1,0,0,0,7,1,0'

	time_list = response_string.split(",")
	t_int = [int(s) for s in time_list]

	# Year, Month, Day, Hour, Min, Sec, Weekday, Yearday, DST from t_int
	# Year, Month, Day, Weekday, Hour, Min, Seconds, Milliseconds to Tuple.
	time_tuple = (t_int[0], t_int[1], t_int[2], t_int[6], t_int[3], t_int[4], t_int[5], 0)
	rtc = machine.RTC()
	rtc.datetime(time_tuple)
	print("Time has been set.")

	# Initialise parameters for measurements
	samples = 100
	history = 25
	future = samples - history - 1
	threshold = 2000
	# Initialise registers and pointer
	output_reg = [0]*samples
	historic_reg = [0]*history
	hist_pointer = 0
	index = 0
	# For machine ID
	UNIQUE_ID = 1337

	print("Begin reading values.")
	# Infinite reading loop
	while True:
		# Take readings
		reading = ads.read(3)
		light = ads.read(2)

		# Intrusion detection
		if light > 1000:
			# Construct JSON, send message.
			intrusion_message = {
				'device_id' : UNIQUE_ID,
				'time' : time.localtime(),
				'intrusion' : 1,
				'intensity' : light,
			}

			send_mqtt(intrusion_message)

		# Shock detection
		if math.fabs(reading) > ads.read(0):
			# Capture time
			shock_time = time.localtime()

			# Turn on cues, visual, audio.
			buzzer.duty(512)
			led.low()

			# Add current reading to output register
			output_reg[history+1] = reading;

			# Fill output register with up-to-date readings
			for future_pointer in range (0,future):
				output_reg[future_pointer+history+1] = ads.read(0)

			# Turn buzzer off
			buzzer.duty(0)

			# Copy history into output register
			output_reg[0:history - hist_pointer] = historic_reg[hist_pointer:history]
			output_reg[history - hist_pointer: history] = historic_reg[0:hist_pointer]

			# Acquire reading statistics for output register
			maximum_value = max(output_reg)
			minimum_value = min(output_reg)
			mean_value = float(sum(output_reg))/float(len(output_reg))

			# Construct JSON, send message.
			shock_message = {
				'device_id' : UNIQUE_ID,
				'index' : index,
				'time' : shock_time,
				'max_value' : maximum_value,
				'mean_value' : mean_value,
				'min_value' : minimum_value,
				'intrusion' : 0,
			}

			send_mqtt(shock_message)

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
