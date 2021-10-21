## How to run:
   
## The setup:
   - 1 Zookeeper 
   - 1 Broker 
   - 1 Topic with 1 partition
   - 1 Consumer
   - 1 Producers

## Report:
- Creates two topics called "events" and "events-output"
- Runs consumer.py which has 1 Consumer and 1 Producer
- Reads kafka configuration from "getting-started.ini" (default: bootstrap.servers = localhost:9092)
- Sample data "stream.gz" is sent to the "events" topic by kafka-console-producer script
- 
##Bonus Questions / Challenges:
  > **Q/C: How do you scale it to improve throughput**?

 - Throughput can be increased by setting up a topic with multiple partitions, 
   with multiple producers writing to them. By analogy on the consumer side,
multiple consumers reading from the partitions. 
> **Q/C: You may want count things for different time frames but only do json parsing once.**

- Storing the "thing count" in a dictionary with key:value pair { date:count }, output to file if necessary 

> **Q/C: Explain how you would cope with failure if the app crashes mid day / mid year.**

- Another instance of the Consumer app could be up and running in parallel at a different location, 
so if one crashed the other can take over

> **Q/C: When creating e.g. per minute statistics, how do you handle frames that arrive late or frames with a random 
timestamp (e.g. hit by a bitflip), describe a strategy?**

- In the case of assuming the "maximum 5 second late" rule,  ------------ TODO
