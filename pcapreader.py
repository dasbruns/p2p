#!/usr/bin/env python

import subprocess
import binascii
from lxml import etree as ET
import os
import argparse


def read(path):
    print('reading..{}'.format(path))
    p = subprocess.Popen(stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                         args=['tshark -T fields -e data -r {}'.format(path)], shell=True)
    out, err = p.communicate()

    print('read')
    out = out.split(b'\n')

    # filter empty
    myout = []
    for msg in out:
        if msg:
            myout.append(msg)

    ref = [b'User-Agent', b'ANNOUNCE', b'SETUP', b'OPTIONS', b'SET_PARAMETER', b'FLUSH', b'RECORD']
    ref = list(map(lambda x: binascii.hexlify(x), ref))
    msgs = []
    for msg in myout:
        for r in ref:
            if r in msg:
                msgs.append(msg)
                break
    return msgs


def dataModel(pit, msgs):
    count = -1
    root = pit.getroot()
    dm = ET.Element('DataModel', name='in')
    dm.append(ET.Element('String', token='false', value='?'))
    root.append(dm)
    for msg in msgs:
        count += 1
        dm = ET.Element('DataModel', name='a{}'.format(count))
        dm.append(ET.Element('Blob', attrib={'value': msg, 'valueType': 'hex'}))
        root.append(dm)
    return pit


def stateModel(pit, num):
    root = pit.getroot()
    sm = ET.Element('StateModel', name='default', initialState='first')
    s = ET.Element('State', name='first')
    myCount = num
    for i in range(num):
        ac = ET.Element('Action', type='output')
        ac.append(ET.Element('DataModel', ref='a{}'.format(num - myCount)))
        s.append(ac)
        ac = ET.Element('Action', type='input')
        ac.append(ET.Element('DataModel', ref='in'))
        s.append(ac)
        myCount -= 1
    sm.append(s)
    root.append(sm)
    return pit


def test(pit, role=False, IP='127.0.0.1', port=36666):
    pit.getroot().append(ET.Element('Test', name='Default'))
    test = pit.find('Test')
    # test.append(ET.Element('Agent', attrib={'ref': 'Local'}))
    test.append(ET.Element('StateModel', attrib={'ref': 'default'}))
    # append default publisher
    if role == True:
        publisher = ET.Element('Publisher', name='test', attrib={'class': 'TcpClient'})
        publisher.append(ET.Element('Param', name='Host', attrib={'value': str(IP)}))
    else:
        publisher = ET.Element('Publisher', name='test', attrib={'class': 'TcpListener'})
        publisher.append(ET.Element('Param', name='Interface', attrib={'value': str(IP)}))
    publisher.append(ET.Element('Param', name='Port', attrib={'value': str(port)}))
    test.append(publisher)
    # append publishing device for random number generating
    test.append(ET.Element('Publisher', name='null', attrib={'class': 'Null'}))
    test.append(ET.Element('Publisher', name='nullOUT', attrib={'class': 'Console'}))
    # append some kind of logger
    logger = ET.Element('Logger', attrib={'class': 'File'})
    logger.append(ET.Element('Param', name='Path', attrib={'value': 'testseries'}))
    test.append(logger)
    return pit


def generateCrash(path, dir, outp):
    msgs = read(path)
    if not msgs:
        print('no messages')
        return
    pit = ET.Element('Peach')
    pit = ET.ElementTree(pit)
    pit = dataModel(pit, msgs)
    pit = stateModel(pit, len(msgs))
    pit = test(pit, True)

    pit.write('{}/{}/recheck{}.xml'.format(outp, dir, 'b' if 'Init' in path else 'a'), pretty_print=True)
    return


def oswalk(inp, outp):
    path = inp
    for DIR in os.listdir(path):
        sub_path = os.path.join(path, DIR)
        print(sub_path)
        # f = open(os.path.join(sub_path, 'PcapMonitor_Monitor_2_NetworkCapture.pcap'), 'r')
        # f.close()
        try:
            os.makedirs(outp + '/{}'.format(DIR))
        except:
            pass
        generateCrash(os.path.join(sub_path, 'PcapMonitor_Monitor_2_NetworkCapture.pcap'), DIR, outp)
        sub_path = os.path.join(sub_path, 'Initial')
        generateCrash(os.path.join(sub_path, 'PcapMonitor_Monitor_2_NetworkCapture.pcap'), DIR, outp)
        if not os.listdir(outp.format(DIR)):
            os.rmdir(outp.format(DIR))


if __name__ == '__main__':
    print('running')
    parser = argparse.ArgumentParser()
    # INPUTpath should be pointing to Peach's log folder, where the folders of crashes reside
    # e.g. logs/yourTest/Faults
    # in this location all the faulty test cases reside each in its own folder named with the iteration number it occured
    parser.add_argument('INPUTpath', help='where to look for files')
    parser.add_argument('OUTPUTpath', help='where to write files')
    args = parser.parse_args()
    oswalk(args.INPUTpath, args.OUTPUTpath)
