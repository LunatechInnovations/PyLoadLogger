#!/bin/python

import serial
import signal, os
import datetime, time

#Global variables
g_run = True

#Setup signal for clean exit on Ctrl+c
def signal_handler(signum, frame):
	g_run = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)

#status_name
#Return a human readable status value based on the character sent on serial port
def status_name(s):
	if s == 'G':
		return "Gross"
	elif s == 'N':
		return "Net"
	elif s == 'U':
		return "Underload"
	elif s == 'O':
		return "Overload"
	elif s == 'M':
		return "Motion"
	elif s == 'E':
		return "Error"

	return "Invalid status"

def main():
	#Setup port
	baudrate = 9600
	device = "/dev/ttyUSB0"
	timeout = 3.0
	xonxoff = False
	parity = serial.PARITY_NONE
	stopbits = serial.STOPBITS_ONE
	bytesize = serial.EIGHTBITS

	port = serial.Serial(device, baudrate, bytesize, parity, stopbits, timeout, xonxoff)

	#Setup output file
	ts = time.time()
	filename = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
	output_file = open(filename, "w")

	#Main loop
	while g_run:
		try:
			rcv = port.read(11)
		except serial.SerialException as e:
			print "Reading aborted"
			break

		weight = int(rcv[1:9])
		status = status_name(rcv[9])
		print "Weight: %d Status: %s" % (weight, status)
		output_file.write("%d\n" % weight)

	port.close()
	output_file.close()

if __name__ == '__main__':
	main()
