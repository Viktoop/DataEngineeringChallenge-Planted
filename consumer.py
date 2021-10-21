#!/usr/bin/env python

import sys
import json
import asyncio
import datetime
import time
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException


# Reading configuration parameters from config file passed as argument
# returns config_dict needed for consumer constructor
#         topics_array for consumer subscription
#         output_topic for producer topic
def read_config_from_ini_file():
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    args = parser.parse_args()

    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)

    consumer_dict = dict(config_parser['consumer'])
    producer_dict = dict(config_parser['default'])
    topics_array = [dict(config_parser['topic'])['topic']]
    prod_output_topic = dict(config_parser['topic'])['output-topic']

    return consumer_dict, producer_dict, topics_array, prod_output_topic


def consume_event(producer, unique_ids, event, output_topic, unique_ids_current_timestamp):
    # read value from topic message object
    # read timestamp from and convert to string in given format YYYY/MM/DD-H:M
    #   to strip all unnecessary data and since operator used is only '=='
    event_value_json = json.loads(event.value())
    event_ts = datetime.datetime.strftime(datetime.datetime.fromtimestamp(event_value_json["ts"]), '%Y/%m/%d-%H:%M')

    # if incoming timestamp is first ever or if  it is equal to current set counting timestamp
    if not unique_ids_current_timestamp or event_ts == unique_ids_current_timestamp:
        unique_ids.add(event_value_json["uid"])

    # if it is not equal it is greater since they are ascending ordered
    else:
        # async produce jsonl to 'output topic', clear out unique ids set, add the incoming unique id
        output_json = {"ts": unique_ids_current_timestamp, "uid_count": len(unique_ids)}

        print(f"Produced to topic '{output_topic}': ", output_json)
        asyncio.run(async_produce(producer, output_topic, output_json))

        unique_ids.clear()
        unique_ids.add(event_value_json["uid"])

    # return the latest event timestamp
    return event_ts


# asynchronous production to output topic
async def async_produce(producer, topic, obj):
    # convert from string representation back to timestamp
    obj['ts'] = int(datetime.datetime.timestamp(datetime.datetime.strptime(obj['ts'], "%Y/%m/%d-%H:%M")))
    producer.produce(topic, json.dumps(obj))
    producer.poll(0)
    producer.flush()


def report_error(event):
    if event.error().code() == KafkaError.PARTITION_EOF:
        sys.stderr.write('%% %s [%d] reached end at offset %d\n' % (event.topic(), event.partition(), event.offset()))
    elif event.error():
        raise KafkaException(event.error())


def shutdown():
    running = False


if __name__ == '__main__':
    running = True
    consumer_config, producer_config, consumer_topics_list, producer_output_topic = read_config_from_ini_file()
    # timestamp for current timestamp for which ids are being counted
    # set of unique ids being counted
    unique_ids_ts = None
    unique_ids_set = set()
    # counter for timing events/frames per second
    events_count = 0

    try:
        consumer_instance = Consumer(consumer_config)
        producer_instance = Producer(producer_config)

        consumer_instance.subscribe(consumer_topics_list)

        reference_time = time.time()
        while running:
            # consume new event/frame from topic
            topic_event = consumer_instance.poll(timeout=5.0)

            # counting consumed events/frames per second
            if topic_event is not None:
                events_count += 1

            # if elapsed time has passed print performance, reset count and time
            if time.time() - reference_time >= 1:
                print(events_count, " ev/sec")
                events_count = 0
                reference_time = time.time()

            # no events/frames within the 5 second window -> send out left over unique ids and clear out for next set
            if topic_event is None and len(unique_ids_set):
                output_json_obj = {"ts": unique_ids_ts, "uid_count": len(unique_ids_set)}
                print(f"Produced to topic '{producer_output_topic}': ", output_json_obj)
                asyncio.run(async_produce(producer_instance, producer_output_topic, output_json_obj))

                unique_ids_set.clear()
                unique_ids_ts = None

            # no events/frames -> continue waiting
            elif topic_event is None:
                continue

            # log error
            elif topic_event.error():
                report_error(topic_event)

            # new event/frame consumed from topic -> calculate unique ids and return timestamp for current unique set
            else:
                unique_ids_ts = consume_event(producer_instance, unique_ids_set, topic_event, producer_output_topic, unique_ids_ts)

    finally:
        consumer_instance.close()
