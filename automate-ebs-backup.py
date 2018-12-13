'''
Created on Nov 13, 2018

@author: vijayakumar.reddiar
'''
import json
import boto3
import datetime

"""
Implements a simple backup strategy for the EC2 instances by automating the EBS snapshot creation and cleanup 
using AWS Lambda services. Implementation leverages the instance tagging for the EBS backup automation. 

Following are the EC2 tags used in this implementation

Name: backup | Backup, Value: User defined description, Mandatory
Name: Retention, Value: <number of days>, Optional
Name: DeleteOn, Value: <deletion date>, Set by this job for cleanup

"""

def lambda_handler(event, context):
    create_ebs_snapshots(event, context)
    cleanup_ebs_snapshots(event, context)
    return {
        'statusCode': 200,
        'body': json.dumps('Completed creating and cleaning up the EBS snapshots')
    }
    
"""
This function creates the snapshot for all the EBS volumes of the EC2 instances with the tag name "backup | Backup" 
It also looks for the optional EC2 instance tag name "Retention" to calculate the snapshot retention days.
During the snapshot creation this function tags the snapshot with the DeleteOn date for the 
automated deletion of snapshots.    
"""
def create_ebs_snapshots(event, context):
    ec2 = boto3.client('ec2')
    
    reservations = ec2.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
        ]
    ).get(
        'Reservations', []
    )
        
    instances = [
        i for r in reservations
        for i in r['Instances']
    ]

    print "Found %d instances that need backing up" % len(instances)
    
    
    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
            retention_days = 7

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print "Found EBS volume %s on instance %s" % (
                vol_id, instance['InstanceId'])

            delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
            delete_fmt = delete_date.strftime('%Y-%m-%d')

            snap = ec2.create_snapshot(
                VolumeId=vol_id, 
                Description='Created by EC2 Automated Backup Job',
                TagSpecifications=[
                        {
                            'ResourceType': 'snapshot',
                            'Tags' : [
                                    {'Key': 'DeleteOn', 'Value': delete_fmt},
                                    {'Key': 'Name', 'Value': 'ec2-backup-snapshot-'+ vol_id}
                                ]
                        }
                    ]
                )

            print "Retaining snapshot %s of volume %s from instance %s for %d days" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
                retention_days,
            )

"""
This function looks at all snapshots that have a "DeleteOn" tag containing
the current day formatted as YYYY-MM-DD. This function should be run at least
daily.
"""
def cleanup_ebs_snapshots(event, context):
    ec2 = boto3.client('ec2')
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account'];
    
    delete_on = datetime.date.today().strftime('%Y-%m-%d')
    filters = [
        {'Name': 'tag-key', 'Values': ['DeleteOn']},
        {'Name': 'tag-value', 'Values': [delete_on]},
    ]
    snapshot_response = ec2.describe_snapshots(OwnerIds=[account_id], Filters=filters)

    for snap in snapshot_response['Snapshots']:
        print "Deleting snapshot %s" % snap['SnapshotId']
        ec2.delete_snapshot(SnapshotId=snap['SnapshotId'])
