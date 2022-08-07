#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import os

import logging
import requests
import serial

logging.basicConfig(format="%(asctime)s %(name)-15s %(levelname)-8s %(message)s", level=20)
log:logging.Logger = logging.getLogger()

def checksum(line:str) -> str:
    return chr((sum(list(line)) & 0x3F) + 0x20)

def parse_frame(frame:bytes, influxdb_url:str) -> bool:
    parsed_values = {}
    linevalues = []
    for dataset in filter(None, frame.split(b'\x0d')):
        dataset = dataset.lstrip(b'\n')
        checksumchar = checksum(dataset[:-1])
        if checksumchar != chr(dataset[-1]):
            log.debug('Checksum error, aborting frame')
            return False
        spline = dataset.split(b'\t')
        log.debug(spline)
        etiquette = spline[0].decode('ascii')
        value = spline[1].decode('ascii')
        timestamp = None
        if len(spline) == 4: # Horodaté
            value = spline[2].decode('ascii')
            timestamp = spline[1].decode('ascii')

        ints = [
            'EAST',
            'EASF',
            'EASD',
            'EAIT',
            'ERQ',
            'IRMS',
            'URMS',
            'PREF',
            'PCOUP',
            'SINST',
            'SMAX',
            'CCA',
            'UMOY',

        ]
        for radix in ints:
            if etiquette.startswith(radix):
                value = int(value)
        quote = '"'
        if isinstance(value, int):
            quote = ""
        linevalues.append('{etiquette}={quote}{value}{quote}'.format(
            etiquette=etiquette,
            value=value,
            quote=quote,
        ))
        parsed_values[etiquette] = {
            'value': value,
            'timestamp': timestamp,
        }

    influx_line = 'teleinfo,ADSC={adsc} {linev}'.format(
        adsc=parsed_values['ADSC']['value'],
        linev=','.join(linevalues),
    )
    try:
        requests.post(influxdb_url, data=influx_line)
    except Exception as exc:
        log.exception('Error while posting data')
        return False
    return True

def main() -> None:
    ser = serial.Serial(
        os.environ.get('SERIAL_PORT', '/dev/ttyAMA0'),
        9600,
        bytesize=7,
        parity=serial.PARITY_EVEN
    )
    influxdb_url = os.environ.get('INFLUXDB_URL', 'http://127.0.0.1:8186/write')
    first_frame = True
    while True:
        frame = ser.read_until(b'\x03')
        if first_frame:
            first_frame = False
            continue
        if frame[0] != 2:
            log.error('Incomplete frame')
            log.debug(frame)
            continue
        parse_frame(frame[1:-1], influxdb_url)


if __name__ == "__main__":
    main()
