"""Create an HDF5 file in memory and retrieve the raw bytes
require python3.7.5 above
"""
import sys
import os
import argparse
import logging

import xml.etree.ElementTree as ET
import h5py

def file_path(string):
    '''
        check whether string is a directory
    '''
    if os.path.isfile(string):
        return string
    raise NotADirectoryError(string)

def dir_path(string):
    '''
        check whether string is a directory
    '''
    if os.path.isdir(string):
        return string
    raise NotADirectoryError(string)

def parser_args():
    '''
    parser arguements
    '''
    parser = argparse.ArgumentParser(description='xml to h5py format convert')
    parser.add_argument('--input', type=file_path, required=True, help='Path to the imput xml file')
    parser.add_argument('--output', type=dir_path, default=".",
                        help='Path to the output h5py folder')
    return parser.parse_args()

def process_xml(opts):
    '''
    process xml to hash
    '''
    summary = ET.parse(opts.input).getroot()[0]
    name_in_report = summary.attrib['name']
    properties = summary[0]
    version = "unknow"
    for _p in properties:
        if _p.attrib['name'] == "version":
            version = _p.attrib['value']
    logging.info(version)
    out_put = os.path.join(opts.output, version + ".h5")
    logging.info(out_put)
    _h5f = h5py.File(out_put, 'a')
    _xmlfh = open(opts.input, 'rb')
    _h5f.attrs[name_in_report] = _xmlfh.read()
    _h5f.close()
    _xmlfh.close()


if __name__ == '__main__':
    sys.stdout.flush()
    logging.basicConfig(level=logging.DEBUG)
    m_opts = parser_args()
    process_xml(m_opts)
