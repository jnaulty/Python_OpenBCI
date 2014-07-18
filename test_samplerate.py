#!/usr/bin/env python2

import serial
import time

s = serial.Serial('/dev/ttyACM1', 115200)
print('serial loaded')

test_text = True

time.sleep(1)

# read intro text
while s.inWaiting():
    print(s.readline())

if test_text:
    s.write('x')
else:
    s.write('b')

# s.write('f')

t = time.time()
print('sleep')
time.sleep(2)
print('done sleeping')
#print(s.inWaiting())
while s.inWaiting() >= 1:
    #s.inWaiting()
    s.read(1)

t = time.time()
print('for real')
time.sleep(0.25)
#print(s.inWaiting())
#c = s.inWaiting() / 39.0
c = 0

while s.inWaiting() >= 1:
    if test_text:
        s.readline()
    else:
        s.read(39)
    c += 1
t2 = time.time()

print(t2 - t)
print(c)
print(c / (t2 - t))
    
s.close()