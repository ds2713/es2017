from machine import Pin, I2C
import ads1x15

i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)

ads = ads1x15.ADS1115(i2c, address=0x49)

value = ads.read(0)

print(value)