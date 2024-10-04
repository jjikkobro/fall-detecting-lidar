import serial
import time

ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=.1)

while True:
    data = ser.readline().decode('utf-8').strip() 
    print(data)

    if data:
        print('turn on')
        break


print('Send Data')
ser.write(2)
time.sleep(3)
while True:
    data = ser.readline().decode('utf-8').strip()
    if data:
        print(data)
    
