set -e
if [[ ! -d venv ]]
then
    echo "Creating virtual environment 'venv' "
    python -m venv venv
    echo "Activating virtual environment 'venv' "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Activating virtual environment 'venv' "
    source venv/bin/activate
fi

if [[ ! -f steam.gz ]]
then
    echo '******************************************************'
    echo "Downloading sample data as 'stream.gz'"
    curl https://tda-public.s3.eu-central-1.amazonaws.com/hire-challenge/stream.jsonl.gz > stream.gz
    echo "Download complete."
else
    echo "Sample data exists as stream.gz"
fi

echo '******************************************************'
echo 'Running docker-compose using docker_compose.yml file'
docker-compose up -d

echo 'Waiting 10s for docker container to come up...'
sleep 10

echo "Creating topic 'events'"
docker compose exec broker \
  kafka-topics --create \
    --topic events \
    --bootstrap-server localhost:9082 \
    --replication-factor 1 \
    --partitions 1

echo "Creating topic 'events-output'"
docker compose exec broker \
  kafka-topics --create \
    --topic events-output \
    --bootstrap-server localhost:9082 \
    --replication-factor 1 \
    --partitions 1

echo '******************************************************'
echo "Producing events/frames from stream.gz to topic 'events'"
echo "Running producer.py (takes ~1 minute depending on machine)"
python producer.py getting_started.ini

echo '...'
echo 'Finished producing.'

echo '******************************************************'



echo "Starting consuming events from topic 'events' consumer.py"

echo "Consumer will not stop consuming.

When ev/sec shows 0 repeatedly close with ctrl + C

Output will be located on topic 'events-output' as json.dumps with real timestamp
Value diplayed here is human readable 
{'ts' : timestamp, 'uid_count' : uid_count}"

python consumer.py getting_started.ini


