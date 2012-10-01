#! /usr/bin/env python

import sys, os
import select, socket, serial
import optparse


# Option parsing, duh
parser = optparse.OptionParser()

parser.add_option('-d',
				'--device',
				help = 'Serial port device',
				dest = 'device',
				default = '/dev/ttyS0')
parser.add_option('-b',
				'--baud',
				help = 'Baud rate',
				dest = 'baudrate',
				type = 'int',
				default = 9600)
parser.add_option('-p',
				'--port',
				help = 'Host port',
				dest = 'port',
				type = 'int',
				default = 23200)

(opts, args) = parser.parse_args()


# Serial port setup
width = 8
parity = 'N'
stopbits = 1
xon = 0
rtc = 0

ttyS = serial.Serial(opts.device, opts.baudrate, width, parity, stopbits, 1, xon, rtc)
ttyS.setTimeout(0) # Non-blocking
ttyS.flushInput()
ttyS.flushOutput()

print >>sys.stderr, 'MUX > Serial port: %s @ %s' % (opts.device, opts.baudrate)


# Server setup
server_address = ('localhost', opts.port)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(server_address)
server.listen(5)

print >>sys.stderr, 'MUX > Server: %s:%d' % server_address


# Poller setup
READ_ONLY = select.POLLIN | select.POLLPRI

poller = select.poll()
poller.register(ttyS, READ_ONLY)
poller.register(server, READ_ONLY)


# Convenience lists
# Easy file descriptor-to-socket dict
fd_to_socket = {ttyS.fileno(): ttyS,
				server.fileno(): server,
				}

# Connected clients list
clients = []


def add_client(client):
	print >>sys.stderr, 'MUX > New connection from', client.getpeername()
	client.setblocking(0)
	fd_to_socket[client.fileno()] = client
	clients.append(client)
	poller.register(client, READ_ONLY)


def remove_client(client, why='?'):
	print >>sys.stderr, 'MUX > Closing %s: %s' % (client.getpeername(), why)
	poller.unregister(client)
	clients.remove(client)
	client.close()


##### MAIN
while True:
	try:
		events = poller.poll(500)

		for fd, flag in events:

			# Get socket from fd
			s = fd_to_socket[fd]

			if flag & (select.POLLIN | select.POLLPRI):

				# A readable server socket is ready to accept a connection
				if s is server:
					connection, client_address = s.accept()
					add_client(connection)

				# Data from serial port
				elif s is ttyS:
					data = s.read(80)
					#print >>sys.stderr, 'MUX > Data from serial:', data
					if clients:	[client.send(data) for client in clients]

				# Data from client
				else:
					data = s.recv(80)
					#print >>sys.stderr, 'MUX > Data from client:', data

					# Client has data
					if data: ttyS.write(data)

					# Interpret empty result as closed connection
					else: remove_client(s, 'Got no data')


			elif flag & select.POLLHUP:
				remove_client(s, 'HUP')


			elif flag & select.POLLERR:
				remove_client(s, 'Received error')


	except (KeyboardInterrupt, SystemExit):
		print >>sys.stderr, '\nMUX > Closing...'
		break;

if clients:
	[client.close() for client in clients]

ttyS.close()
server.close()

print >>sys.stderr, 'MUX > Done! =)'
