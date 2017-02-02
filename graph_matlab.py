import serial

def main():
	#Attempt connection
	try:
		serialport = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.5)

	# For the Macs
	except:
		serialport = serial.Serial("/dev/tty.SLAB_USBtoUART", 115200, timeout=0.5)

	# Confirm success at reaching this stage.
	print("Connection successful.")

	# Data stored here.
	f = open("data.csv", "w+")

	# Read input string from serial.
	while True:
		command = str(serialport.readlines())
		print(command)

		# If it's a new measurement, then record down.
		if command[3:6] == "New":
			new_data = command[21:len(command)-7]
			f.write(str(new_data))
			f.write("\r\n")

if __name__ == '__main__':
	main()
