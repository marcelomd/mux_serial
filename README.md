# mux_serial

Serial port multiplexer over TCP.


## What?

This is a set of simple utilities used to let several programs share access to a device connected to a single serial port.
Included:
* A server, which manages the serial port and shares it over TCP with any number of clients;
* a client, used to interact with the connected device (either via text terminal or via script);
* and a logger, which receives a copy of everything going through the serial port and timestamps it.


## So, how?

The way I use it:

1. Launch the server:
  ```bash
  stormbreaker:mux_serial> ./mux_server.py -d /dev/ttyACM0 -b 115200 -p 23200
  MUX > Serial port: /dev/ttyACM0 @ 115200
  MUX > Server: 127.0.0.1:23200
  MUX > Use ctrl+c to stop...

  MUX > New connection from ('127.0.0.1', 37581)
  MUX > New connection from ('127.0.0.1', 37582)
  ```

2. Then connect any number of clients:
  ```bash
  stormbreaker:mux_serial> ./mux_client.py -p 23200
  MUX > Connected to localhost:23200
  MUX > Use ctrl+] to stop...

  0,0,0
  0,0,0
  0,0,0
  370,317,0
  239,241,0
  ```

3. ...and the logger:
  ```bash
  stormbreaker:mux_serial> ./mux_logger.py -p 23200 -f log
  MUX > Logging output to log
  MUX > Connected to localhost:23200
  MUX > format: [date time elapsed delta] line
  MUX > Use ctrl+c to stop...

  [2013-02-28 23:05:28 0.000 0.000] 0,0,0
  [2013-02-28 23:05:29 0.303 0.303] 0,0,0
  [2013-02-28 23:05:29 0.602 0.299] 0,0,0
  [2013-02-28 23:05:29 0.901 0.299] 370,317,0
  [2013-02-28 23:05:30 1.442 0.541] 239,241,0
  ```

4. Now I have a console on one terminal and one logger on the other. Optionally I would launch some script to interact with the device on a third terminal, like this:
  ```python
  from mux_client import MuxClient

  client = MuxClient()
  client.run()

  while True:
      client.term.sendline('bla')
      client.term.expect('bleh', timeout = 10)
  client.close()
```

Some useful info:
* The arguments are optional. The defaults are `/dev/ttyS0` at `9600bps` served at `localhost:23200`;

* In theory the server can accept external connections. Could be useful to monitor a device connected to a remote machine;

* The client is built on top of the `fdpexpect` module;

* If launched with `python -i`, the client enters the interactive shell upon exit and gives access to a MuxClient instance:
  ```bash
  stormbreaker:mux_serial> python -i ./mux_client.py -p 23200
  MUX > Connected to localhost:23200
  MUX > Use ctrl+] to stop...

  >>> t = client.term
  >>> client.term.sendline('')
  1
  >>> client.term.expect(',', timeout = 10)
  0
  >>> client.term.before
  '197'
  ```

* There are other ways to connect to the client. Any TCP socket will do:
  ```bash
  stormbreaker:mux_serial> socat -,raw,echo=0,escape=0x0f TCP:localhost:23200
  196,195,0
  ```

* I used the `SerialCallResponseASCII` Arduino sketch for this demo.


## But why?

I had a need to automate some tests for an embedded system I was developing. I could not easily leave an script running agains this system and have accurate timing information on the logs. Also, it was impossible to access the user shell to investigate something while the test ran.


## Credits

Code for the logger was shamefully stolen from [Grabserial](http://elinux.org/Grabserial)


