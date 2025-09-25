# Example Code from Blue Robotics
# https://github.com/bluerobotics/ping-python/blob/master/examples/ping360AutoScan.py

from brping import definitions
from brping import Ping360
import time
import argparse

from builtins import input

import pickle

import os

## Parse Command line options
############################

parser = argparse.ArgumentParser(description="Ping360 auto scan example")
parser.add_argument('--device', action="store", required=False, type=str, help="Ping device port. E.g: /dev/ttyUSB0")
parser.add_argument("--num_runs", action='store', required=False, default=1, type=int)
parser.add_argument('--output_location', action="store", required=True, type=str, help="Directory to save data")
parser.add_argument('--baudrate', action="store", type=int, default=2000000, help="Ping device baudrate. E.g: 115200")
parser.add_argument('--udp', action="store", required=False, type=str, help="Ping UDP server. E.g: 192.168.2.2:9090")
args = parser.parse_args()
if args.device is None and args.udp is None:
    parser.print_help()
    exit(1)

# Make a new Ping360
myPing360 = Ping360()
if args.device is not None:
    myPing360.connect_serial(args.device, args.baudrate)
elif args.udp is not None:
    (host, port) = args.udp.split(':')
    myPing360.connect_udp(host, int(port))

if myPing360.initialize() is False:
    print("Failed to initialize Ping!")
    exit(1)

print("------------------------------------")
print("Ping360 auto scan..")
print("Press CTRL+C to exit")
print("------------------------------------")

input("Press Enter to continue...")

myPing360.control_auto_transmit(
    mode = 1,
    gain_setting = 0,
    transmit_duration = 80,
    sample_period = 80,
    transmit_frequency = 750,
    number_of_samples = 1024,
    start_angle = 0,
    stop_angle = 400,
    num_steps = 1,
    delay = 0
)

#Make Output dir
os.mkdir(args.output_location)

# Print the scanning head angle
for i in range (args.num_runs):
    os.mkdir(f"{args.output_location}/{i}")
    for n in range(400):
        m = myPing360.wait_message([definitions.PING360_AUTO_DEVICE_DATA])
        if m:
            print(m.angle)
            f = open(f"{args.output_location}/{i}/angle{m.angle}.bin", 'wb')
            pickle.dump(m,f)
            f.close()
        time.sleep(0.001)

# if it is a serial device, reconnect to send a line break
# and stop auto-transmitting
if args.device is not None:
    myPing360.connect_serial(args.device, args.baudrate)

# turn the motor off
myPing360.control_motor_off()