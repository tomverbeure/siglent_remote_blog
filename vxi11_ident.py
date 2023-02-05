#! /usr/bin/env python3

import sys
import vxi11

instr = vxi11.Instrument(sys.argv[1])
print(instr.ask("*IDN?"))


