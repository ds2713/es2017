from machine import Pin, I2C
import ads1x15

# print('Hello world!')

#Set up software I2C bus with device.
i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
#Look for I2C devices
i2cAddress = i2c.scan()
# print('Address: ', i2cAddress)
numBytes = 1

ads = ads1x15.ADS1115(i2c, address=72)

# i2c.writeto(i2cAddress, bytes([0x01,0x82,0x83])) #write config register
# i2c.writeto(i2cAddress, bytes([0x00]))
# value = i2c.readfrom(i2cAddress, numBytes)

# reading_low = value[0]
# reading_high = value[1]

# print('Low:		', value)
# print('High:	', reading_high)

# while True:

value = list()

for x in range (0,100):

	value.append(ads.read(0))


print(value)
