#! /usr/bin/env python

import os, sys
import socket
import optparse
import time

# Option parsing, duh
parser = optparse.OptionParser()

parser.add_option('-p', '--port',
				help = 'Host port',
				dest = 'port',
				type = 'int',
				default = 23200)
parser.add_option('-f', '--file',
				help = 'Output file',
				dest = 'file',
				type = 'string')

(opts, args) = parser.parse_args()


# Helpers
def flush():
	sys.stdout.flush()

def _write_simple(x):
	sys.stdout.write(x)

def _write_log(x):
	sys.stdout.write(x)
	log.write(x)


# Setup log file writing
if opts.file:
	logname = opts.file
	log	= open(logname, 'w')
	print >>sys.stderr, 'MUX > Logging output to', logname
	write = _write_log

else:
	write = _write_simple


# Setup client
server_address = ('localhost', opts.port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(server_address)


print >>sys.stderr, 'MUX > Connected to %s:%d' % server_address
print >>sys.stderr, 'MUX > format: [date time elapsed delta] line'
print >>sys.stderr, 'MUX > Use ctrl+c to stop...\n'


# Init line catcher
base_t = 0
line_t = 0
prev_t = 0

newline = True
current_line = ''


##### MAIN
while True:
	try:
		# Read 1 char
		x = s.recv(1)

		# Ignore carriage returns
		if x == '\r':
			continue

		# Set base_t to when first char is received
		if not base_t:
			base_t = time.time()

		if newline:
			line_t = time.time()
			date = time.localtime(line_t)
			elapsed = line_t - base_t
			delta = elapsed - prev_t
			write('[%04d-%02d-%02d %02d:%02d:%02d %4.3f %4.3f] '
					%  (date.tm_year, date.tm_mon, date.tm_mday,
						date.tm_hour, date.tm_min, date.tm_sec,
						elapsed, delta))
			prev_t = elapsed
			newline = False

		# Print it!
		write(x)
		current_line += x

		if x == '\n':
			newline = True
			current_line = ''
		flush()

	except:
		break

print >>sys.stderr, '\nMUX > Closing...'

s.close()
if opts.file:
	log.close()

print >>sys.stderr, 'MUX > Done! =)'
