## Consumer.py
Example app that sends a POST request to the Dataflow APIs to generate a topic and then subscribes to that topic, printing the messages in an endless loop.

## Requirements
- **requests**, to send the post request;
- **confluent_kafka**, to receive the messages	;
- **proton**, to read the messages.

## Run
`python3 consumer.py`
