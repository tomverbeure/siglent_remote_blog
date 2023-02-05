#! /usr/bin/env python3

import argparse
import pyvisa

def fetch_waveform_descriptor(scope, channel_nr):
    #scope.write(f"C{channel_nr}:WAVEFORM? DESC")
    scope.write(f"MATH:WAVEFORM? DESC")
    desc = scope.read_raw(500)
    print(desc)

    # When issing the Cx:WF? DESC command, an SD2304X is supposed to return 368 bytes.
    # But on mine, it alternately returns 368 and 369 bytes, where the 369th byte is
    # always 0x0a. This is probably one of the many bugs in the Siglent remote control
    # software stack.
    if len(desc) not in [368, 369]:
        raise RunTimeError(f"Unexpected channel waveform descriptor length ({len(desc)})")

    return desc

def parse_waveform_header(info, desc):
    ofs = 0

    header_type = desc[ofs:desc.index(ord(','))].decode("utf-8")
    ofs += len(header_type) + 1

    pound_nine = desc[ofs:ofs+2].decode("utf-8")
    ofs += 2
    if pound_nine != "#9":
        raise RunTimeError(f"Expected '#9' after header type")

    block_length = desc[ofs:ofs+9].decode("utf-8")
    ofs += 9
    block_length = int(block_length)

    info['header_type']  = header_type
    info['block_length'] = block_length

    return desc[ofs:]

def parse_string(desc, max_len):
    string = desc[0:max_len].decode("utf-8")
    string = string[:string.index('\x00')]
    desc = desc[max_len:]

    return string, desc

def parse_waveform_descriptor(desc): 
    info = {}
    desc = parse_waveform_header(info, desc)
    ofs = 0

    descriptor_name, desc = parse_string(desc, 16)
    info['descriptor_name'] = descriptor_name

    template_name, desc = parse_string(desc, 16)
    info['template_name'] = template_name

    print(info, len(desc))

    print(desc[ofs:])

def fetch_waveform_data(scope, channel_nr):
    scope.write(f"C{channel_nr}:WF? DAT2")
    data = scope.read_raw(150000000)
    print(len(data))

if __name__ == '__main__':

    parser = argparse.ArgumentParser( description='Waveform data from a Siglent oscilloscope.')
    #parser.add_argument('--output', '-o', dest='filename', required=True, help='the output filename')
    parser.add_argument('device', metavar='DEVICE', nargs=1, help='the ip address or hostname of the oscilloscope')
    
    args = parser.parse_args()

    rm = pyvisa.ResourceManager('')
    scope = rm.open_resource('TCPIP::%s' % args.device[0])
    scope.read_termination = None

    desc = fetch_waveform_descriptor(scope, 1)
    parse_waveform_descriptor(desc)
    fetch_waveform_data(scope,1)

    #screendump(args.device[0], args.filename)

