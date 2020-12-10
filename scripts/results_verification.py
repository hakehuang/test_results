#!/usr/bin/env python3
#
#  Maciej Perkowski / Hake Huang
#

"""result file content check
example usage:
    $ python results_verification.py -P board.xml -V 1
"""

from pathlib import Path
from argparse import ArgumentParser
import urllib.request as urllib
import json
import logging
import xml.etree.ElementTree as ET


def check_file_size(file_path, max_size=5):
    """
    Check if the file size of a given file is smaller than max_size.

    :param file_path: path of junit xml report from sanitycheck to be checked
    :param max_size: max size allowed for the given file
    """
    file_size = file_path.stat().st_size / 1024 / 1024
    return bool(file_size <= max_size)


def check_name(file_path):
    """
    Check if the name of the file corresponds with the platform name in the report

    :param file_path: path of junit xml report from sanitycheck to be checked
    """
    platform = file_path.name[:-4]
    summary = ET.parse(file_path).getroot()[0]
    name_in_report = summary.attrib['name']
    return bool(platform == name_in_report)


def check_attribute_value(file_path=None, item=None, max_value=None):
    """
    Check if the value of a given attribute is smaller than max_count. Attribute can be e.g. 'errors' or 'failures'

    :param file_path: path of junit xml report from sanitycheck to be cheched
    :param item: attribute to be verified
    :param max_value: max value of the given attribute
    """
    summary = ET.parse(file_path).getroot()[0]
    item_count = int(summary.attrib[item])
    return bool(item_count <= max_value)


def check_version(file_path=None, version=0):
    """
    Check if zephyr's version given in the report match the expected one

    :param file_path: junit xml report from sanitycheck
    :param version: check version or not
    """
    if version == 0:
        return True

    url_version = "https://testing.zephyrproject.org/daily_tests/versions.json"

    data = urllib.urlopen(url_version).read()
    versions_json = json.loads(data)
    version_list = []
    for _x in versions_json:
        if type(_x).__name__ == 'string':
            version_list.append(_x)
        elif type(_x).__name__ == 'dict':
            version_list.append(_x['version'])


    testsuite = ET.parse(file_path).getroot()[0]
    properties = testsuite[0]
    for property in properties:
        if property.attrib['name'] == "version":
            return bool(property.attrib['value'] in version_list)

    print("Version not found.")
    return False


def parse_args():
    """Parse and return required limits from arguments"""
    argpar = ArgumentParser(description='Verifies if a given report fulfils requirements before its publishing')
    argpar.add_argument('-P', '--path', required=True, type=str, help='Path to the report which will be verified')
    argpar.add_argument('-V', '--version', required=True, default=0, type=int, help='enable version check')
    argpar.add_argument('-S', '--max-size', default='5', type=float, help='Maximum size of a file that is accepted')
    argpar.add_argument('-E', '--max-errors', default='50', type=int, help='Maximum accepted number'
                                                                           ' of errors in the report')
    argpar.add_argument('-F', '--max-failures', default='50', type=int, help='Maximum accepted number'
                                                                             ' of failures in the report')
    return argpar.parse_args()


def main(args):
    file_path = Path(args.path)

    logging.basicConfig(level=logging.DEBUG, format='[%(filename)s:%(lineno)d] %(relativeCreated)6d %(threadName)s %(message)s')

    if not file_path.exists():
        print(f"XML report not found at {file_path}")
        raise FileNotFoundError
    try:
        assert file_path.name.endswith(".xml"), "Not an XML file given"
        assert check_name(file_path), "Report name does not match the platform name given in the report"
        assert check_version(file_path, args.version), "Incorrect version of zephyr"
        assert check_file_size(file_path, args.max_size) / 1024 / 1024, \
            f"Size of the XML report at {file_path} is >{args.max_size} Mb"
        assert check_attribute_value(file_path, 'failures', args.max_failures), \
            f"XML report at {file_path} has too many failures (>{args.max_failures}. It requires manual verification.)"
        assert check_attribute_value(file_path, 'errors', args.max_errors), \
            f"XML report at {file_path} has too many errors (>{args.max_errors}. It requires manual verification.)"
    except AssertionError as ex:
        print(ex)
        exit(1)

    print(f"Report {args.path} verified.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    main(args)
