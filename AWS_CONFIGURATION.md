# AWS Configuration Guide for OpenAg-DB

This document outlines the necessary AWS resources, IAM roles, policies, and secrets required for deploying OpenAg-DB infrastructure.

## Table of Contents

- [Overview](#overview)
- [S3 Buckets](#s3-buckets)
- [IAM Roles](#iam-roles)
- [IAM Policies](#iam-policies)
- [GitHub Secrets](#github-secrets)
- [Security Best Practices](#security-best-practices)
- [Environment Configuration](#environment-configuration)

## Overview

OpenAg-DB uses the following AWS services:

- **S3**: Data lake storage (Iceberg tables), scraper artifacts, frontend static hosting
- **Lambda** (future): Serverless API deployment
- **CloudFront** (optional): CDN for frontend and API
- **IAM**: Authentication and authorization using OIDC

### Architecture Components

1. **Data Storage**: Apache Iceberg tables stored in S3
2. **API Backend**: FastAPI application (deployed to Lambda or ECS)
3. **Frontend**: React static site (deployed to S3 + CloudFront or GitHub Pages)
4. **Scrapers**: Scheduled jobs via GitHub Actions writing to S3

## S3 Buckets

### Recommended Bucket Names

Following AWS naming best practices (lowercase, hyphenated, globally unique):

#### 1. Data Lake Bucket (Iceberg Tables)
```
openagdb-datalake-<environment>-<region>
```

**Examples:**
- `openagdb-datalake-prod-us-east-1`
- `openagdb-datalake-dev-us-east-1`

**Purpose**: Stores Apache Iceberg tables with equipment data

**Configuration:**
- **Versioning**: Enabled (for data lineage and recovery)
- **Encryption**: AES-256 (SSE-S3) or AWS KMS
- **Lifecycle Policy**: Transition old versions to Glacier after 90 days
- **Public Access**: Blocked (all 4 settings)

#### 2. Artifacts Bucket (Scraper Outputs)
```
openagdb-artifacts-<environment>-<region>
```

**Examples:**
- `openagdb-artifacts-prod-us-east-1`
- `openagdb-artifacts-dev-us-east-1`

**Purpose**: Stores scraper logs, temporary data, and processing artifacts

**Configuration:**
- **Versioning**: Optional (for debugging)
- **Encryption**: AES-256 (SSE-S3)
- **Lifecycle Policy**: Delete objects after 30 days
- **Public Access**: Blocked (all 4 settings)

#### 3. Frontend Bucket (Optional - if not using GitHub Pages)
```
openagdb-frontend-<environment>
```

**Examples:**
- `openagdb-frontend-prod`
- `openagdb-frontend-dev`

**Purpose**: Static site hosting for React frontend

**Configuration:**
- **Versioning**: Enabled (for rollback capability)
- **Encryption**: AES-256 (SSE-S3)
- **Static Website Hosting**: Enabled
- **Public Access**: Allow GetObject only (via bucket policy)

## IAM Roles

### 1. GitHub Actions Deployment Role (OIDC)

**Role Name**: `GitHubActionsDeploymentRole-OpenAgDB`

**Trust Policy** (allows GitHub Actions OIDC authentication):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:adam133/equipment-testing:*"
        }
      }
    }
  ]
}
```

**Note**: Replace `<AWS_ACCOUNT_ID>` with your actual AWS account ID.

**Setup Requirements:**
1. Create OIDC identity provider in IAM for `token.actions.githubusercontent.com`
2. Audience should be `sts.amazonaws.com`
3. Restrict to specific repository: `adam133/equipment-testing`

### 2. Scraper Execution Role

**Role Name**: `OpenAgDB-ScraperRole`

**Trust Policy**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:adam133/equipment-testing:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### 3. API Backend Role (Lambda or ECS)

**Role Name**: `OpenAgDB-APIRole`

**Trust Policy** (for Lambda):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## IAM Policies

### 1. Scraper Policy (Minimum Permissions)

**Policy Name**: `OpenAgDB-ScraperPolicy`

**Purpose**: Allows scrapers to write data to S3 buckets

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "WriteToDataLake",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1/*",
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1"
      ]
    },
    {
      "Sid": "WriteArtifacts",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-artifacts-prod-us-east-1/*"
      ]
    },
    {
      "Sid": "IcebergTableOperations",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1/warehouse/*",
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1/warehouse"
      ]
    }
  ]
}
```

**Attach to**: `OpenAgDB-ScraperRole`

### 2. API Backend Policy (Read-Only Data Access)

**Policy Name**: `OpenAgDB-APIPolicy`

**Purpose**: Allows API to read from Iceberg tables via DuckDB/PyIceberg

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadDataLake",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1/*",
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1"
      ]
    },
    {
      "Sid": "IcebergMetadataRead",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1/warehouse/*/metadata/*"
      ]
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:<AWS_ACCOUNT_ID>:log-group:/aws/lambda/openagdb-api:*"
    }
  ]
}
```

**Attach to**: `OpenAgDB-APIRole`

### 3. Frontend Deployment Policy

**Policy Name**: `OpenAgDB-FrontendDeploymentPolicy`

**Purpose**: Allows GitHub Actions to deploy static frontend to S3

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3FrontendDeployment",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-frontend-prod/*",
        "arn:aws:s3:::openagdb-frontend-prod"
      ]
    },
    {
      "Sid": "CloudFrontInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "arn:aws:cloudfront::<AWS_ACCOUNT_ID>:distribution/*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Project": "OpenAgDB"
        }
      }
    }
  ]
}
```

**Attach to**: `GitHubActionsDeploymentRole-OpenAgDB`

### 4. Combined Deployment Policy

**Policy Name**: `OpenAgDB-FullDeploymentPolicy`

**Purpose**: Comprehensive deployment permissions for CI/CD pipeline

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3DataLakeAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-datalake-*/*",
        "arn:aws:s3:::openagdb-datalake-*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:ResourceAccount": "<AWS_ACCOUNT_ID>"
        }
      }
    },
    {
      "Sid": "S3ArtifactsAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-artifacts-*/*",
        "arn:aws:s3:::openagdb-artifacts-*"
      ]
    },
    {
      "Sid": "S3FrontendAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::openagdb-frontend-*/*",
        "arn:aws:s3:::openagdb-frontend-*"
      ]
    },
    {
      "Sid": "CloudFrontManagement",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Project": "OpenAgDB"
        }
      }
    }
  ]
}
```

**Attach to**: `GitHubActionsDeploymentRole-OpenAgDB`

## GitHub Secrets

Configure the following secrets in your GitHub repository (`Settings` → `Secrets and variables` → `Actions`):

### Required Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AWS_ACCOUNT_ID` | Your AWS account ID | `123456789012` |
| `AWS_REGION` | Primary AWS region | `us-east-1` |
| `AWS_DEPLOYMENT_ROLE_ARN` | ARN of GitHub Actions OIDC role | `arn:aws:iam::123456789012:role/GitHubActionsDeploymentRole-OpenAgDB` |
| `S3_DATALAKE_BUCKET` | Data lake bucket name | `openagdb-datalake-prod-us-east-1` |
| `S3_ARTIFACTS_BUCKET` | Artifacts bucket name | `openagdb-artifacts-prod-us-east-1` |
| `S3_FRONTEND_BUCKET` | Frontend bucket name (if applicable) | `openagdb-frontend-prod` |

### Optional Secrets (for enhanced features)

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID | `E1234567890ABC` |
| `API_DOMAIN` | Custom domain for API | `api.openagdb.org` |
| `FRONTEND_DOMAIN` | Custom domain for frontend | `openagdb.org` |

### Environment Variables (Not Secrets)

These can be set as GitHub variables (not secrets) as they are not sensitive:

| Variable Name | Description | Example Value |
|---------------|-------------|---------------|
| `ENVIRONMENT` | Deployment environment | `production` or `development` |
| `ICEBERG_CATALOG_NAME` | Iceberg catalog name | `ag_equipment` |
| `ICEBERG_NAMESPACE` | Iceberg namespace | `ag_equipment` |

## Security Best Practices

### 1. Principle of Least Privilege

- **Scrapers**: Only write permissions to specific S3 paths
- **API**: Only read permissions to data lake
- **Deployment**: Time-limited OIDC tokens (default 10 min)

### 2. S3 Bucket Security

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1/*",
        "arn:aws:s3:::openagdb-datalake-prod-us-east-1"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::openagdb-datalake-prod-us-east-1/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

### 3. OIDC Configuration

**Audience Validation**: Always set `aud` to `sts.amazonaws.com`

**Subject Claim Validation**: Restrict to specific repository and optionally branch:

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
  },
  "StringLike": {
    "token.actions.githubusercontent.com:sub": "repo:adam133/equipment-testing:ref:refs/heads/main"
  }
}
```

### 4. CloudWatch Logging

Enable CloudWatch logging for all components:

- **API Lambda**: Automatic with Lambda execution role
- **Scrapers**: Send logs to CloudWatch Logs via GitHub Actions
- **S3 Access**: Enable S3 access logging to separate audit bucket

### 5. Encryption

- **Data at Rest**: Enable S3 default encryption (AES-256 or KMS)
- **Data in Transit**: Enforce HTTPS-only access (SSL/TLS)
- **Secrets**: Use AWS Secrets Manager for sensitive credentials (if needed)

### 6. Network Security

- **API**: Use API Gateway with throttling and WAF (when deployed to Lambda)
- **S3**: VPC endpoints for private access (if using ECS/EC2)
- **CloudFront**: Use Origin Access Identity (OAI) or Origin Access Control (OAC)

### 7. Monitoring and Alerting

Set up CloudWatch alarms for:

- Unauthorized S3 access attempts
- IAM role assumption failures
- Scraper execution failures
- API error rates > threshold

## Environment Configuration

### Development Environment

**Buckets:**
- `openagdb-datalake-dev-us-east-1`
- `openagdb-artifacts-dev-us-east-1`

**IAM Roles:**
- `GitHubActionsDeploymentRole-OpenAgDB-Dev`
- `OpenAgDB-ScraperRole-Dev`

**GitHub Environment**: `development`

### Production Environment

**Buckets:**
- `openagdb-datalake-prod-us-east-1`
- `openagdb-artifacts-prod-us-east-1`
- `openagdb-frontend-prod`

**IAM Roles:**
- `GitHubActionsDeploymentRole-OpenAgDB`
- `OpenAgDB-ScraperRole`
- `OpenAgDB-APIRole`

**GitHub Environment**: `production`

**Additional Security:**
- Required reviewers for deployments
- Branch protection rules
- Manual approval for production deployments

## Frontend-Backend OIDC Communication (Future)

For secure communication between frontend and backend using OIDC:

### Option 1: Amazon Cognito (Recommended)

1. **User Pool**: Create Cognito User Pool for user authentication
2. **Identity Pool**: Federate with GitHub/Google/etc.
3. **Frontend**: Use AWS Amplify SDK for authentication
4. **Backend**: Validate JWT tokens from Cognito

**Benefits:**
- Managed service (no custom auth logic)
- Built-in user management
- MFA support
- Social identity providers

### Option 2: Custom OIDC with Auth0/Okta

1. **Auth Provider**: Use Auth0 or Okta as identity provider
2. **Frontend**: Implement OIDC client flow
3. **Backend**: Validate JWT tokens from provider

**Benefits:**
- More control over authentication flow
- Can integrate with existing enterprise SSO
- Richer user profile management

### Implementation Notes

- **Token Storage**: Store JWT in httpOnly cookies (not localStorage)
- **CORS**: Configure proper CORS headers on API
- **Token Refresh**: Implement refresh token rotation
- **API Authorization**: Use JWT claims for role-based access control (RBAC)

## Setup Checklist

- [ ] Create OIDC identity provider in AWS IAM for GitHub Actions
- [ ] Create S3 buckets with proper naming and configuration
- [ ] Create IAM roles with trust policies
- [ ] Attach IAM policies to roles
- [ ] Configure bucket policies for security
- [ ] Add GitHub secrets to repository
- [ ] Test OIDC authentication from GitHub Actions
- [ ] Enable CloudWatch logging
- [ ] Set up monitoring and alerting
- [ ] Document custom domain setup (if applicable)
- [ ] Test scraper deployment
- [ ] Test API deployment
- [ ] Test frontend deployment

## Terraform Configuration (Optional)

For infrastructure-as-code approach, consider using Terraform to provision these resources. A sample module structure:

```
terraform/
├── modules/
│   ├── s3-buckets/
│   ├── iam-roles/
│   ├── iam-policies/
│   └── cloudfront/
├── environments/
│   ├── dev/
│   └── prod/
└── main.tf
```

## Additional Resources

- [AWS IAM OIDC Identity Providers](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Apache Iceberg on AWS](https://iceberg.apache.org/aws/)
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [AWS Lambda Security](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)

## Questions or Issues?

For questions about AWS configuration, please open an issue on the [GitHub repository](https://github.com/adam133/equipment-testing/issues).
