from matplotlib.pyplot import plot, draw, show, ion, clf, close
import serial

serialport = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.5)

while True:

	command = str(serialport.readlines())

	if len(command)>2:
		# clf()
		# close(1)
		# print("If")
		new_data = command[21:len(command)-7]
		# print(new_data)

		listy = [int(s) for s in new_data.split(',')]

		print(listy)
		# ion()
		plot(listy)
		draw()
		show()
		# show(block=False)
		# plt.show()

# plt.plot([1,2,3,4])
# plt.ylabel('some numbers')
# plt.show()
