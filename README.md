<b>Raspberry Pi FM receiver using Python 3 I2C and Tea5767</b>

Contributor: Dipto Pratyaksa
<a href="http://www.linuxcircle.com">LinuxCircle.com</a>

Description:

This is a simple TEA5767 driver to tune into a local radio station
with Raspberry Pi 2.

<img src="tea5767.png" />

Running Instruction:

run tea5767stationscanner.py with Phyton 3 this way:
sudo python3 tea5767stationscanner.py

or if you prefer bash command:

make the file executable:

sudo chmod +x tea5767stationscanner.py

run it:

sudo ./tea5767stationscanner.py

You can also use the controller to take user input:

sudo python3 tea5767controller.py

or with sufficient permission and executable file:
sudo ./tea5767controller.py

17 August 2015 update
Added web interface.
Run it with: sudo python3 radio_server.py
Open browser from a client computer: http://IPADDRESSOFYOURPI:10005
Example: http:/192.168.1.2:10005

