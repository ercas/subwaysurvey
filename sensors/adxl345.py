#!/usr/bin/env python3

import serial
import sys
import time

OUTPUT = "adxl345_%d.csv" % time.time()

device_file = sys.argv[1]
adxl345 = serial.Serial(
    device_file,
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    xonxoff = False
)

print("writing data to %s" % OUTPUT)
with open(OUTPUT, "w") as f:
    f.write("TIME,X,Y,Z\n")
    while True:
        try:
            line = "%f,%s" % (
                time.time(), adxl345.readline().rstrip().decode()
            )
            if ("X" in line):
                pass
            else:
                f.write("%s\n" % line)
                print(line)
        except KeyboardInterrupt:
            break
        except UnicodeDecodeError:
            pass
