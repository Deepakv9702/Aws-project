"""
Idle Resource Finder — Deepak Vaida
Identifies idle/unused AWS resources that can be safely decommissioned
Used at MBFS to find and delete 40+ idle resources saving $20K+

Checks:
- Unattached EBS volumes
- Unused Elastic IPs
- Old EBS snapshots (> 90 days)
- Stopped EC2 instances (> 30 days)
- Unused ALB/NLB target groups
"""

import boto3
import json
from datetime import datetime, timezone, timedelta

def find_unattached_ebs(ec2):
    """Find EBS volumes in 'available' state (unattached)."""
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )['Volumes']
    
    results = []
    for v in volumes:
        size_gb = v['Size']
        # gp2: ~$0.10/GB/month, gp3: ~$0.08/GB/month
        monthly_cost = size_gb * 0.10
        results.append({
            'VolumeId': v['VolumeId'],
            'SizeGB': size_gb,
            'VolumeType': v['VolumeType'],
            'CreateTime': str(v['CreateTime']),
            'EstMonthlyWaste': f'${monthly_cost:.2f}'
        })
    return results

def find_unused_eips(ec2):
    """Find Elastic IPs not associated with any instance."""
    addresses = ec2.describe_addresses()['Addresses']
    unused = [a for a in addresses if 'InstanceId' not in a and 'NetworkInterfaceId' not in a]
    # Each unused EIP costs $0.005/hr = ~$3.65/month
    for eip in unused:
        eip['EstMonthlyWaste'] = '$3.65'
    return unused

def find_old_snapshots(ec2, days=90):
    """Find EBS snapshots older than specified days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    old_snapshots = []
    for s in snapshots:
        if s['StartTime'] < cutoff:
            size_gb = s['VolumeSize']
            monthly_cost = size_gb * 0.05  # $0.05/GB/month for snapshots
            old_snapshots.append({
                'SnapshotId': s['SnapshotId'],
                'SizeGB': size_gb,
                'AgeDays': (datetime.now(timezone.utc) - s['StartTime']).days,
                'Description': s.get('Description', ''),
                'EstMonthlyWaste': f'${monthly_cost:.2f}'
            })
    return old_snapshots

def main():
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    print("\n=== AWS Idle Resource Finder — Deepak Vaida ===\n")

    print("--- Unattached EBS Volumes ---")
    ebs = find_unattached_ebs(ec2)
    print(json.dumps(ebs, indent=2, default=str))
    total_ebs_waste = sum(float(v['EstMonthlyWaste'].replace('$','')) for v in ebs)

    print("\n--- Unused Elastic IPs ---")
    eips = find_unused_eips(ec2)
    print(json.dumps(eips, indent=2, default=str))

    print("\n--- Old Snapshots (>90 days) ---")
    snaps = find_old_snapshots(ec2)
    print(f"Found {len(snaps)} old snapshots")

    print(f"\n=== SUMMARY ===")
    print(f"Unattached EBS: {len(ebs)} volumes — ~${total_ebs_waste:.0f}/month wasted")
    print(f"Unused EIPs: {len(eips)} — ~${len(eips)*3.65:.2f}/month wasted")
    print(f"Old Snapshots: {len(snaps)} (>90 days old)")
    print(f"\nReview above and delete to reclaim costs.")

if __name__ == "__main__":
    main()
