from kafka import KafkaProducer
import json
import sys
import urllib.request
import gzip
import shutil
import logging
import os

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


setting_absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


try:
    topic=sys.argv[1]
except IndexError:
    logging.error('----------------------------------------------------------------')
    logging.error('You need to specify an existing topic as an argument at runtime.')
    logging.error('Something like :')
    logging.error('python3 producer.py topicname')
    logging.error('----------------------------------------------------------------')
    raise


producer = KafkaProducer(
    value_serializer=lambda m: json.dumps(m).encode('utf-8'),
    bootstrap_servers=['localhost:9092'])

url = 'http://tx.tamedia.ch.s3.amazonaws.com/challenge/data/stream.jsonl.gz'

logging.info('Downloading data from http://tx.tamedia.ch.s3.amazonaws.com/challenge/data/stream.jsonl.gz')

urllib.request.urlretrieve(url, setting_absolute_path + '/data_to_load/data_sample.jsonl.gz')

logging.info('Data downloaded to /data_to_load/data_sample.jsonl.gz')
logging.info('This may take some minutes....')
logging.info('A bit annoying, right?')


with gzip.open( setting_absolute_path + '/data_to_load/data_sample.jsonl.gz', 'rb') as f_in:
    with open( setting_absolute_path + '/data_to_load/data_sample.jsonl', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


logging.info('Producer is reading the file now')

with open(setting_absolute_path + '/data_to_load/data_sample.jsonl', 'r') as json_file:
    json_list = list(json_file)

for json_item in json_list:

    try:
        result = json.loads(json_item)
    except:
        result = dict({'error': 'Not Json Object'})
    finally:
        producer.send(topic, value=result)