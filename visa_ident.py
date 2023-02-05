#! /usr/bin/env python3

import sys
import pyvisa

rm = pyvisa.ResourceManager()
siglent = rm.open_resource(f"TCPIP::{sys.argv[1]}")
print(siglent.query('*IDN?'))

