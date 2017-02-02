from machine import Pin, I2C
import ads1x15
import time
import math
import network
from umqtt.simple import MQTTClient

def main():

	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	sta_if.connect('EEERover', 'exhibition')
	time.sleep(5)

	print(sta_if.ifconfig())

    import uftpd

	CLIENT_ID = 'mdma'# machine.unique_id()
	CLIENT_TOPIC = '/esys/mdma'
	client = MQTTClient(CLIENT_ID, '192.168.0.10')
	client.connect()
	client.publish(CLIENT_TOPIC, bytes('MDMA live', 'utf-8'))

	i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
	i2cAddress = i2c.scan()
	numBytes = 1

	samples = 100
	history = 25
	future = samples - history - 1
	threshold = 50

	ads = ads1x15.ADS1115(i2c, address=72)

	value = [0]*samples
	historic_reading = [0]*history
	reading_pointer = 0
	hist_pointer = 0

	while True:

		reading = ads.read(0)

		if math.fabs(reading) > threshold:

			maximum_value = 0

			for x in range (0, history):
				value[x] = historic_reading[(hist_pointer+1)%history]
				hist_pointer = (hist_pointer+1)%history

			value[history+1] = reading;

			for future_pointer in range (0,future):
				value[future_pointer+history+1] = ads.read(0)

			print('New measurement: ', value)

			for x in range (0, samples):
				if value[x] > maximum_value:
					maximum_value = value[x]

			output_str = str('Max reading:', maximum_value)

			client.publish(CLIENT_TOPIC, bytes(output_str, 'utf-8'))

		else:

			historic_reading[hist_pointer] = reading
			hist_pointer = (hist_pointer+1)%history

if __name__ == "__main__":
    # execute only if run as a script


    
    main()
   
# except:
# 	print('Stopped')

