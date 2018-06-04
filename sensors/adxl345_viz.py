#!/usr/bin/env python3

from matplotlib import pyplot
import colorama
import serial
import sys
import time

OUTPUT = "adxl345_%d.csv" % time.time()
THRESH = 20
GRAPH_WIDTH = 70

device_file = sys.argv[1]
adxl345 = serial.Serial(
    device_file,
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    xonxoff = False
)

with open(OUTPUT, "w") as f:
    while True:
        try:
            line = adxl345.readline().rstrip().decode()
            if ("X" in line):
                pass
            else:
                (x, y, z) = line.split(",")
                line = "%f,%s,%s,%s" % (
                    time.time(), x, y, z
                )
                f.write("%s\n" % line)

                (x_float, y_float, z_float) = map(
                    lambda n: abs(float(n)),
                    (x, y, z)
                )
                (x_width, y_width, z_width) = map(
                    lambda n: int(n / THRESH * GRAPH_WIDTH) - 1,
                    (x_float, y_float, z_float)
                )
                print(
                    colorama.Fore.RED
                    + ("% 6.2f | " % x_float)
                    + ("█" * x_width)
                )
                print(
                    colorama.Fore.GREEN
                    + ("% 6.2f | " % y_float)
                    + ("█" * y_width)
                )
                print(
                    colorama.Fore.BLUE
                    + ("% 6.2f | " % z_float)
                    + ("█" * z_width)
                )
                #print(line)
        except KeyboardInterrupt:
            break
        except UnicodeDecodeError:
            pass
        except ValueError:
            pass
