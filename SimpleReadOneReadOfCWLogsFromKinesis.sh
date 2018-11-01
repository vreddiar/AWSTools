#!/bin/bash
PROFILE_NAME=$1
STREAM_NAME=$2
LIMIT=1
aws kinesis get-records --profile $PROFILE_NAME --limit $LIMIT --shard-iterator $(aws kinesis get-shard-iterator --profile $PROFILE_NAME --stream-name $STREAM_NAME --shard-iterator-type TRIM_HORIZON --shard-id  $(aws kinesis describe-stream --profile $PROFILE_NAME --stream-name $STREAM_NAME | jq -r .StreamDescription.Shards[].ShardId) | jq -r ."ShardIterator") | jq -r .Records[].Data | base64 -d | zcat
