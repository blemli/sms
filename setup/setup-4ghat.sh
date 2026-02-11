#!/bin/bash
set -e
echo "~~~ Setting up SIM7600E-H 4G HAT ~~~"

echo "~~~ Enable serial port hardware ~~~"
sudo raspi-config nonint do_serial_hw 0

echo "~~~ Disable serial console (frees /dev/ttyS0) ~~~"
sudo raspi-config nonint do_serial_cons 1

echo "~~~ Install minicom for manual testing ~~~"
sudo apt install -y minicom

echo "~~~ Add user to dialout group ~~~"
sudo usermod -aG dialout pi

echo "~~~ Test modem (after reboot) ~~~"
echo "Run: minicom -D /dev/serial0 -b 115200"
echo "Type: AT (should respond OK)"
echo "Type: AT+CPIN? (check SIM status)"
echo "Type: AT+CSQ (signal strength, 10-31 is good)"
echo ""
echo "To send test SMS:"
echo "  AT+CMGF=1"
echo "  AT+CMGS=\"+41791234567\""
echo "  Hello World<Ctrl+Z>"

echo "~~~ Reboot required for serial changes ~~~"
read -p "Reboot now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then sudo reboot; fi
