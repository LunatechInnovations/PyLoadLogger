#!/bin/python

import serial
import datetime, time
import curses
import os.path
import sys
import matplotlib.pyplot as plt

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

def setup_port(port):
	port.baudrate = 9600
	port.port = "/dev/ttyUSB0"
	port.timeout = 3.0
	port.xonxoff = False
	port.parity = serial.PARITY_NONE
	port.stopbits = serial.STOPBITS_ONE
	port.bytesize = serial.EIGHTBITS
	port.rtscts = False
	port.write_timeout = 10.0
	port.dsrdtr = False

def close_curses():
	curses.nocbreak()
	curses.echo()
	curses.nocbreak()
	curses.endwin()

def error_exit(msg):
	close_curses()
	print >> sys.stderr, msg
	sys.exit(1)

def main():
	#TODO handle command line arguments
	#Setup port
	port = serial.Serial()
	setup_port(port)
	if not os.path.exists(port.port):
		error_exit("File not found: %s" % port.port)

	print "Opening port: %s" % port.port
	port.open()

	#Setup output file
	ts = time.time()
	filename = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
	output_file = open(filename, "w")

	#Setup curses
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	stdscr.nodelay(True)

	#Setup plot data
	data = []
	time = []
	current_time = 0

	#Main loop
	while stdscr.getch() != 27:
		#Synchronize messages
		errcounter = 0
		try:
			while port.read(1) != chr(2):
				errcounter += 1
				#Received 100 characters none of them equal to STX
				if errcounter >= 99:
					break


			rcv = port.read(10)
		except serial.SerialException as e:
			error_exit("Error reading from serial port.")
			break

		if errcounter >= 99:
			error_exit("Error reading from serial port. STX flag not found")
			break

		#Fetch values
		if rcv[9] != chr(3):
			error_exit("Error reading from serial port. ETX flag not found")
			break

		weight = int(rcv[0:8].replace(" ", ""))
		status = status_name(rcv[8])

		#Add plot data
		data.append(weight)
		time.append(current_time)
		current_time += 0.1

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

	#Clean up serial port
	port.close()

	#Clean up output file
	output_file.close()

	#Clean up curses
	close_curses()

	#Show plot
	plt.title('Dragprov')
	plt.ylabel('Kraft Kg')
	plt.xlabel('Tid min')
	plt.grid(True)
	plt.plot(time, data)
	plt.show()

if __name__ == '__main__':
	main()
