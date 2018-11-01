#!/bin/bash
PROFILE_NAME=$1
STREAM_NAME=$2
LIMIT=1
aws kinesis describe-stream --stream-name $STREAM_NAME --profile $PROFILE_NAME --output text | grep SHARDS | awk '{print $2}' |
while read shard;
do
  aws kinesis get-shard-iterator --stream-name $STREAM_NAME --shard-id $shard --shard-iterator-type TRIM_HORIZON --profile $PROFILE_NAME --output text |
  while read iterator;
  do
      while output=`aws kinesis get-records --limit $LIMIT --shard-iterator $iterator --profile $PROFILE_NAME --output text`;
      do iterator=`echo "$output" | head -n1 | awk '{print $2}'`;
          echo "$output" | awk 'NR > 1' | grep RECORDS |
          while read record;
          do echo $record | awk '{print $3}' | base64 -d | zcat;
          done;
      done;
   done;
done
