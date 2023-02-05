#! /usr/bin/env python3

import argparse
import pyvisa
import struct

def fetch_waveform_descriptor(scope, channel_nr):
    scope.write(f"C{channel_nr}:WAVEFORM? DESC")
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

    return string, desc[max_len:]

def parse_double(desc):
    double = struct.unpack('d', desc[0:8])[0]

    return double, desc[8:]

def parse_float(desc):
    f = struct.unpack('f', desc[0:4])[0]

    return f, desc[4:]

def parse_enum(desc):
    enum = struct.unpack('<h', desc[0:2])[0]
    return enum, desc[2:]

def parse_long(desc):
    long = struct.unpack('<I', desc[0:4])[0]
    return long, desc[4:]

def parse_word(desc):
    word = struct.unpack('<h', desc[0:2])[0]
    return word, desc[2:]

def parse_byte(desc):
    word = struct.unpack('B', desc[0:1])[0]
    return word, desc[1:]

def parse_waveform_descriptor(desc): 
    info = {}
    desc = parse_waveform_header(info, desc)
    ofs = 0

    descriptor_name, desc = parse_string(desc, 16)
    info['descriptor_name'] = descriptor_name

    template_name, desc = parse_string(desc, 16)
    info['template_name'] = template_name

    comm_type, desc  = parse_enum(desc)
    info['comm_type'] = comm_type

    comm_order, desc = parse_enum(desc)
    info['comm_order'] = comm_order

    wave_desc_len, desc = parse_long(desc)
    info['wave_desc_len'] = wave_desc_len

    user_text_len, desc = parse_long(desc)
    info['user_text_len'] = user_text_len

    res_desc1_len, desc = parse_long(desc)
    info['res_desc1_len'] = res_desc1_len

    trigtime_array_len, desc = parse_long(desc)
    info['trigtime_array_len'] = trigtime_array_len

    ris_time_array_len, desc = parse_long(desc)
    info['ris_time_array_len'] = ris_time_array_len

    res_array1_len, desc = parse_long(desc)
    info['res_array1_len'] = res_array1_len

    wave_array_1_len, desc = parse_long(desc)
    info['wave_array_1_len'] = wave_array_1_len

    wave_array_2_len, desc = parse_long(desc)
    info['wave_array_2_len'] = wave_array_2_len

    res_array2_len, desc = parse_long(desc)
    info['res_array1_len'] = res_array2_len

    res_array3_len, desc = parse_long(desc)
    info['res_array1_len'] = res_array3_len

    instrument_name, desc = parse_string(desc, 16)
    info['instrument_name'] = instrument_name

    instrument_number, desc = parse_long(desc)
    info['instrument_number'] = instrument_number

    trace_label, desc = parse_string(desc, 16)
    info['trace_label'] = trace_label

    reserved1, desc = parse_word(desc)
    reserved2, desc = parse_word(desc)

    wave_array_count, desc = parse_long(desc)
    info['wave_array_count'] = wave_array_count

    pnts_per_screen, desc = parse_long(desc)
    info['pnts_per_screen'] = pnts_per_screen

    first_valid_pnt, desc = parse_long(desc)
    info['first_valid_pnt'] = first_valid_pnt

    last_valid_pnt, desc = parse_long(desc)
    info['last_valid_pnt'] = last_valid_pnt

    first_point, desc = parse_long(desc)
    info['first_point'] = first_point

    sparsing_factor, desc = parse_long(desc)
    info['sparsing_factor'] = sparsing_factor

    segment_index, desc = parse_long(desc)
    info['segment_index'] = segment_index

    subarray_count, desc = parse_long(desc)
    info['subarray_count'] = subarray_count

    sweeps_per_ack, desc = parse_long(desc)
    info['sweeps_per_ack'] = sweeps_per_ack

    points_per_pair, desc = parse_word(desc)
    info['points_per_pair'] = points_per_pair

    pair_offset, desc = parse_word(desc)
    info['pair_offset'] = pair_offset

    vertical_gain, desc = parse_float(desc)
    info['vertical_gain'] = vertical_gain

    vertical_offset, desc = parse_float(desc)
    info['vertical_offset'] = vertical_offset

    max_value, desc = parse_float(desc)
    info['max_value'] = max_value

    min_value, desc = parse_float(desc)
    info['min_value'] = min_value

    nominal_bits, desc = parse_word(desc)
    info['nominal_bits'] = nominal_bits

    num_subarray_count, desc = parse_word(desc)
    info['num_subarray_count'] = num_subarray_count

    horiz_interval, desc = parse_float(desc)
    info['horiz_interval'] = horiz_interval

    horiz_offset, desc = parse_double(desc)
    info['horiz_offset'] = horiz_offset

    pixel_offset, desc = parse_double(desc)
    info['pixel_offset'] = pixel_offset

    vertunit, desc = parse_string(desc, 48)
    info['vertunit'] = vertunit

    horunit, desc = parse_string(desc, 48)
    info['horunit'] = horunit

    horiz_uncertainty, desc = parse_float(desc)
    info['horiz_uncertainty'] = horiz_uncertainty

    trigger_time_sec, desc = parse_double(desc)
    info['trigger_time_sec'] = trigger_time_sec

    trigger_time_min, desc = parse_byte(desc)
    info['trigger_time_min'] = trigger_time_min

    trigger_time_hour, desc = parse_byte(desc)
    info['trigger_time_hour'] = trigger_time_hour

    trigger_time_day, desc = parse_byte(desc)
    info['trigger_time_day'] = trigger_time_day

    trigger_time_month, desc = parse_byte(desc)
    info['trigger_time_month'] = trigger_time_month

    trigger_time_year, desc = parse_word(desc)
    info['trigger_time_year'] = trigger_time_year

    reserved, desc = parse_word(desc)

    acq_duration, desc = parse_float(desc)
    info['acq_duration'] = acq_duration

    record_type, desc = parse_enum(desc)
    info['record_type'] = record_type

    processing_done, desc = parse_enum(desc)
    info['processing_done'] = processing_done

    reserved5, desc = parse_word(desc)

    ris_sweep5, desc = parse_word(desc)
    info['ris_sweep5'] = ris_sweep5

    timebase, desc = parse_enum(desc)
    info['timebase'] = timebase

    vert_coupling, desc = parse_enum(desc)
    info['vert_coupling'] = vert_coupling

    probe_att, desc = parse_float(desc)
    info['probe_att'] = probe_att

    fixed_vert_gain, desc = parse_enum(desc)
    info['fixed_vert_gain'] = fixed_vert_gain

    bandwidth_limit, desc = parse_enum(desc)
    info['bandwidth_limit'] = bandwidth_limit

    vertical_vernier, desc = parse_float(desc)
    info['vertical_vernier'] = vertical_vernier

    acq_vert_offset, desc = parse_float(desc)
    info['acq_vert_offset'] = acq_vert_offset

    wave_source, desc = parse_enum(desc)
    info['wave_source'] = wave_source

    # TODO: process optional additional blocks

    print(info, len(desc))

    return info

def fetch_waveform_data(scope, channel_nr):
    scope.write(f"C{channel_nr}:WF? DAT2")
    data = scope.read_raw(150000000)
    print(len(data))

    #print(data)

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

