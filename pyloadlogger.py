#!/bin/python

import serial
import datetime, time
import curses

#Global variables
g_run = True

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
	#Setup curses
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	stdscr.nodelay(True)

	#TODO handle command line arguments
	#Setup port
	baudrate = 9600
	device = "/dev/ttyUSB0"
	read_timeout = 3.0
	xonxoff = False
	parity = serial.PARITY_NONE
	stopbits = serial.STOPBITS_ONE
	bytesize = serial.EIGHTBITS
	rtscts = False
	write_timeout = 10.0
	dsrdtr = True
	

	port = serial.Serial(device, baudrate, bytesize, parity, stopbits, read_timeout, xonxoff, rtscts, write_timeout, dsrdtr)

	#Setup output file
	ts = time.time()
	filename = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
	output_file = open(filename, "w")

	#Main loop
	while stdscr.getch() != 27:
		#Synchronize messages
		errcounter = 0
		while port.read(1) != chr(2):
			errcounter += 1
			#Received 100 characters none of them STX
			if errcounter >= 99:
				stdscr.addstr(0, 0, "Error reading from serial port. STX flag not found")
				stdscr.refresh()
				return 0

		rcv = port.read(10)


		#Fetch values
		if rcv[9] != chr(3):
			stdscr.addstr(0, 0, "Error reading from serial port. ETX flag not found")
			stdscr.refresh()
			break;

		weight = int(rcv[0:8].replace(" ", ""))
		status = status_name(rcv[8])

		#Update screen
		stdscr.addstr(0, 0, "Press escape to quit")
		stdscr.addstr(2, 0, "Reading from: %s" % port.port)
		stdscr.addstr(3, 0, "Logging to file: %s" % filename)
		stdscr.addstr(5, 0, "Weight: %13dkg" % weight)
		stdscr.addstr(6, 0, "Status: %15s" % status)
		stdscr.addstr(7, 0, "")
		stdscr.refresh()

		#Append value to file
		output_file.write("%d\n" % weight)

	#Clean up
	port.close()
	output_file.close()

	curses.nocbreak()
	curses.echo()
	curses.nocbreak()
	curses.endwin()


if __name__ == '__main__':
	main()
