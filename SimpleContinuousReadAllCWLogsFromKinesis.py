import boto3
import pprint
import gzip
import StringIO
import time

pp = pprint.pprint
STREAM_NAME = 'YourStream' #Set it to the actual interested stream name
RECORD_LIMIT = 1 #Set this between 1 to 10,000 limit for a batch read
AWS_PROFILE_NAME = 'AWSProfileName' #Set it to the interested AWS profile name from ~/.aws/credentials file

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
kinesis_client = session.client('kinesis')
while True:
    describe_stream_response = kinesis_client.describe_stream(StreamName=STREAM_NAME)
    shard_ids = describe_stream_response['StreamDescription']['Shards']
    if len(shard_ids) < 1:
        break
    for shard_id in shard_ids:
        shard_id = describe_stream_response['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator_response = kinesis_client.get_shard_iterator(StreamName=STREAM_NAME, ShardId=shard_id, ShardIteratorType='TRIM_HORIZON')
        shard_iterator = shard_iterator_response['ShardIterator']
        records_response = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=RECORD_LIMIT)
        while 'NextShardIterator' in records_response:
            for record in records_response['Records']:
                fio = StringIO.StringIO(record['Data'])
                file = gzip.GzipFile(fileobj=fio)
                pp(file.read())
            records_response = kinesis_client.get_records(ShardIterator=records_response['NextShardIterator'], Limit=RECORD_LIMIT)

            time.sleep(5) #sleep for 5 seconds before reading next batch
    time.sleep(15*60) #No more records in kinesis, sleep for 15 minutes before read

