# AWS Serverless Cloud Cost Optimization with EventBridge
Automated cloud cost optimization project that identifies and removes stale EBS snapshots using AWS Lambda, with weekly scheduling via EventBridge and email alerts through SNS.

<br> 

## Detailed Project Overview

Modern cloud environments often accumulate unused infrastructure resources over time. One of the most common hidden cost drivers in AWS environments is orphaned or stale Amazon EBS snapshots.

Snapshots continue to incur storage costs even when:

- The original volume has been deleted

- The volume is no longer attached to a running EC2 instance

- The snapshot is no longer required for operational recovery

Without automated governance, these unused snapshots lead to:

- Increased monthly storage bills

- Reduced infrastructure visibility

- Operational inefficiency

<br>

## Project Objective

The primary objective of this project is to design and implement a secure, automated, and enterprise-ready cost optimization framework that:

- Identifies stale or orphaned EBS snapshots

- Notifies resource owners 24 hours before deletion

- Provides a review window to prevent accidental data loss

- Automatically deletes confirmed unused snapshots

- Maintains full audit visibility and monitoring

This solution follows a safe automation-first approach rather than aggressive deletion.

<br>

## Solution Design

The project was designed using the following principles:

#### 1. Serverless Architecture

The system uses AWS Lambda to avoid infrastructure overhead and ensure scalability.

#### 2. Dual-Phase Safe Deletion

Instead of immediate deletion, the workflow includes:

- Phase 1: Pre-cleanup SNS notification (T-24 hours)

- Phase 2: Cleanup execution after validation

This reduces operational risk.

#### 3. Least Privilege Security Model

- IAM roles are configured with only the minimum permissions required.

- No administrative or unnecessary access is granted.

#### 4. Automated Scheduling

- Amazon EventBridge Scheduler triggers both notification and cleanup phases automatically.

#### 5. Observability & Auditability

- All operations are logged in Amazon CloudWatch.

- Deletion summaries are sent via Amazon SNS.

<br>


## End-to-End Workflow
#### Phase 1 – 24-Hour Advance Notification

- EventBridge triggers Lambda.

- Lambda scans for stale snapshots.

- SNS sends a detailed email listing snapshots scheduled for deletion.

Snapshot owners can:

- Create backups if required

- Add protection tags (e.g., DoNotDelete=True)

- Investigate before deletion

#### Phase 2 – Cleanup Execution

- EventBridge triggers cleanup Lambda.

- Lambda revalidates snapshot status.

- Skips snapshots with protection tags.

- Deletes confirmed stale snapshots.

- Sends post-cleanup summary report.

- Logs all activities in CloudWatch.

<br>


## Security & Governance Approach

#### This project strictly follows:

Least Privilege IAM Access

Zero unnecessary permissions

No wildcard administrative access

Controlled API-level access

Tag-based protection capability

This significantly reduces the attack surface and aligns with AWS security best practices.

<br>


## Business Impact

#### By implementing this solution:

Unused snapshot storage costs are reduced

Manual cleanup effort is eliminated

Infrastructure hygiene is maintained continuously
