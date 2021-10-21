## How to run:
   - Clone GitHub repo to a directory of choice
   - Make sure docker is running
   - Zookeeper will run with container name 'zookeeper7' on 2181 (should be free)
   - Make sure port 9082 is not being used
   - Broker will run with container name 'broker7' on port '9082:9082' with address ://localhost:9082
   - Open Terminal in that directory  
   - Run the application with following command 
>$ ./run.sh

## The setup:
   - 1 Zookeeper 
   - 1 Broker 
   - 2 Topics with 1 partition each
   - 1 Consumer
   - 2 Producers

## Report of what run.sh does:
- Creates virtual environment 'venv' if it does not exist and activates it
- Downloads the given sample data into 'stream.gz' file if it doesn't exist
- Creates docker container using docker_compose.yml
- Creates two topics called "events" and "events-output"
- Runs producer.py which has 1 Producer, and it places sample data into 'events' topic
- Runs consumer.py which has 1 Consumer and 1 Producer consuming from 'events', producing to 'events-output'
##Bonus Questions / Challenges:
  > **Q/C: How do you scale it to improve throughput**?

 - Throughput can be increased by setting up a topic with multiple partitions, 
   with multiple producers writing to them. By analogy on the consumer side,
multiple consumers reading from the partitions. 

> **Q/C: Explain how you would cope with failure if the app crashes mid-day / mid-year.**

- Another instance of the Consumer app could be up and running in parallel at a different location, 
so if one crashed the other can take over

> **Q/C: What did you do? what was the reasons you did it like that?**

- Consumed events/frames one by one. Take out its timestamp and save it for reference as year/month/day/hour/minute, 
create a set for unique ids and add event.uid to the set. A set is a structure containing only unique values.
For every following event with the timestamp belonging to the reference timestamp, add to the set.
Since events are ordered, at the moment an event arrives with a timestamp from the 
following minute, send out timestamp and unique id count to production and update the reference timestamp and reset unique sets.

> **Q/C: Document your approach on how you decide when to output the data**

- Data is outputted as soon as an event with a greater timestamp arrives, marking the previous unique set complete.
 In other words, no more events belonging to the previous timestamp will arrive.


> **Q/C: Awareness of the mechanisms and costs of serialization. Explain (and ideally prove!) 
why json is an ideal format here or why not and then suggest a better solution.**

- Researched Avro structure, but for this specific data sample it would not be much of an impact on size/speed 
since the sample data doesn't have a repeating and constant data structure.
Avro uses a schema in the header to define data types of fields of its data block/s.


