"""
EC2 Auto-Scheduler — Deepak Vaida
Stops dev/staging EC2 instances at 7 PM, starts at 8 AM (Mon-Fri)
Saves ~$50,000/year at MBFS (14 hrs/day × 5 days × instances)

Deploy as AWS Lambda + EventBridge (cron schedules)
"""

import boto3
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_instances_by_tag(ec2, tag_key, tag_value, states):
    """Get EC2 instances with specific tag and state."""
    response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': states}
        ]
    )
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances

def lambda_handler(event, context):
    """
    EventBridge triggers:
    - Stop:  cron(0 13 ? * MON-FRI *)  → 7 PM IST / 1 PM UTC
    - Start: cron(0 2 ? * MON-FRI *)   → 8 AM IST / 2 AM UTC
    """
    action = event.get('action', 'stop')
    regions = os.environ.get('REGIONS', 'us-east-1,us-west-2').split(',')
    env_tags = os.environ.get('ENVIRONMENTS', 'dev,staging').split(',')

    total_affected = 0

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region.strip())

        for env in env_tags:
            if action == 'stop':
                instances = get_instances_by_tag(ec2, 'Environment', env.strip(), ['running'])
                if instances:
                    ec2.stop_instances(InstanceIds=instances)
                    logger.info(f"STOPPED {len(instances)} instances in {region} [{env}]: {instances}")
                    total_affected += len(instances)

            elif action == 'start':
                instances = get_instances_by_tag(ec2, 'Environment', env.strip(), ['stopped'])
                if instances:
                    ec2.start_instances(InstanceIds=instances)
                    logger.info(f"STARTED {len(instances)} instances in {region} [{env}]: {instances}")
                    total_affected += len(instances)

    return {
        'statusCode': 200,
        'body': f'{action.upper()} completed. Total instances affected: {total_affected}'
    }
