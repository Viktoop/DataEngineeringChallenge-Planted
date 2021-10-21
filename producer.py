#!/usr/bin/env python

import sys
import json
from random import choice
import gzip
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    args = parser.parse_args()

    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])
    topic = dict(config_parser['topic'])['topic']

    producer = Producer(config)

    with gzip.open('./stream.gz', 'rb') as json_file:
        line = json_file.readline().decode("utf-8")
        count = 0
        while line:
            if count >= 100000:
                producer.flush()
                count = 0
            else:
                count += 1
            producer.produce(topic, line)
            line = json_file.readline().decode("utf-8")
            producer.poll(0)
        producer.flush()