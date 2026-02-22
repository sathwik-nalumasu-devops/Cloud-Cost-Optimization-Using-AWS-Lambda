import boto3
import logging
from datetime import datetime, timedelta, timezone

# AWS Clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

# SNS Topic ARN
TOPIC_ARN = "arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:YOUR_TOPIC_NAME"

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Tag Keys
PENDING_TAG = "PendingDeletionDate"
PROTECT_TAG = "DoNotDelete"

def lambda_handler(event, context):
    
    # Mode can be: "notify" or "cleanup"
    mode = event.get("mode", "notify")
    
    today = datetime.now(timezone.utc).date()
    deleted_snapshots = []
    notified_snapshots = []
    
    response = ec2.describe_snapshots(OwnerIds=['self'])
    
    for snapshot in response['Snapshots']:
        
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')
        tags = {tag['Key']: tag['Value'] for tag in snapshot.get('Tags', [])}
        
        # Skip protected snapshots
        if tags.get(PROTECT_TAG) == "True":
            continue
        
        # Check if snapshot is stale
        is_stale = False
        
        if not volume_id:
            is_stale = True
        else:
            try:
                volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                
                if not volume_response['Volumes'][0]['Attachments']:
                    is_stale = True
                    
            except ec2.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    is_stale = True
        
        if not is_stale:
            continue
        
        # -------------------------
        # PHASE 1: NOTIFICATION MODE
        # -------------------------
        if mode == "notify":
            
            if PENDING_TAG not in tags:
                
                ec2.create_tags(
                    Resources=[snapshot_id],
                    Tags=[{'Key': PENDING_TAG, 'Value': str(today)}]
                )
                
                notified_snapshots.append(snapshot_id)
        
        # -------------------------
        # PHASE 2: CLEANUP MODE
        # -------------------------
        elif mode == "cleanup":
            
            pending_date_str = tags.get(PENDING_TAG)
            
            if pending_date_str:
                pending_date = datetime.strptime(pending_date_str, "%Y-%m-%d").date()
                
                if today >= pending_date + timedelta(days=1):
                    
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots.append(snapshot_id)
    
    # SNS Notification Logic
    
    if mode == "notify" and notified_snapshots:
        
        message = (
            "EBS Snapshot Pre-Deletion Notice (24 Hours Prior)\n\n"
            f"The following snapshots are marked for deletion after 24 hours:\n\n"
            + "\n".join(notified_snapshots) +
            "\n\nIf these snapshots are required, please add tag: DoNotDelete=True"
        )
        
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="EBS Snapshot Cleanup - 24 Hour Warning",
            Message=message
        )
        
        logger.info("Pre-deletion SNS notification sent.")
    
    
    if mode == "cleanup" and deleted_snapshots:
        
        message = (
            "EBS Snapshot Cleanup Report\n\n"
            f"Deleted Snapshots:\n\n"
            + "\n".join(deleted_snapshots)
        )
        
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="EBS Snapshot Cleanup Completed",
            Message=message
        )
        
        logger.info("Cleanup SNS notification sent.")
    
    return {
        "statusCode": 200,
        "body": f"{mode} phase completed successfully."
    }