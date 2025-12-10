# Example Code from Blue Robotics
# https://github.com/bluerobotics/ping-python/blob/master/examples/ping360AutoScan.py

from brping import definitions
from brping import Ping360
import time
import argparse

from builtins import input

from datetime import datetime

## Parse Command line options
############################

parser = argparse.ArgumentParser(description="Ping360 auto scan example")
parser.add_argument('--device', action="store", required=False, type=str, help="Ping device port. E.g: /dev/ttyUSB0")
parser.add_argument('--baudrate', action="store", type=int, default=2000000, help="Ping device baudrate. E.g: 115200")
parser.add_argument('--udp', action="store", required=False, type=str, help="Ping UDP server. E.g: 192.168.2.2:9090")
parser.add_argument('--duration', action="store", required=False, default=5, type=int, help="Duration to collect data for in seconds")
args = parser.parse_args()
if args.device is None and args.udp is None:
    parser.print_help()
    exit(1)

# Make a new Ping360
sonar_object = Ping360()
if args.device is not None:
    sonar_object.connect_serial(args.device, args.baudrate)
elif args.udp is not None:
    (host, port) = args.udp.split(':')
    sonar_object.connect_udp(host, int(port))

if sonar_object.initialize() is False:
    print("Failed to initialize Ping!")
    exit(1)

test_duration = args.duration

print("------------------------------------")
print("Ping360 Single Beam Data Collection")
print("Press CTRL+C to exit")
print("------------------------------------")

input("Press Enter to continue...")

ping_sonar = sonar_object.control_transducer(
    mode = 1,
    gain_setting = 0,
    angle = 0,
    transmit_duration = 80,
    sample_period = 80,
    transmit_frequency = 750,
    number_of_samples = 1024,
    transmit=True,
    reserved = False
)

SAMPLE_FREQUENCY = 10
ping_time = 0

while True:
    if datetime.now().timestamp() < ping_time+test_duration: #

        if datetime.now().timestamp() >= ping_time+1/SAMPLE_FREQUENCY:
            ping_time = datetime.now().timestamp()
            ping_sonar()
            while datetime.now().timestamp() < ping_time+1/SAMPLE_FREQUENCY
                message = sonar_object.wait_message([definitions.PING360_DEVICE_DATA])



# if it is a serial device, reconnect to send a line break
# and stop auto-transmitting
if args.device is not None:
    myPing360.connect_serial(args.device, args.baudrate)
